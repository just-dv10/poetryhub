from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .models import (
    CustomUser, Poem, Like, Comment, GENRE_CHOICES,
    Conversation, DirectMessage, ChatGroup, GroupMessage,
    EmailVerificationToken
)
from .forms import (
    RegisterForm, LoginForm, PoemForm, CommentForm, ProfileEditForm,
    GroupCreateForm, GroupMessageForm, DirectMessageForm
)


# ─── Auth Views ────────────────────────────────────────────────────────────────

def auth_view(request):
    """Combined login + register on one animated page."""
    if request.user.is_authenticated:
        return redirect('feed')

    reg_form = RegisterForm()
    log_form = LoginForm()
    mode = request.GET.get('mode', 'login')   # 'login' or 'register'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            reg_form = RegisterForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save()
                user.is_email_verified = False
                user.save()
                # Create verification token and send email
                token_obj, _ = EmailVerificationToken.objects.get_or_create(user=user)
                _send_verification_email(request, user, token_obj)
                return render(request, 'auth/email_verification_sent.html', {'email': user.email})
            mode = 'register'

        elif action == 'login':
            log_form = LoginForm(request.POST)
            if log_form.is_valid():
                email = log_form.cleaned_data['email']
                password = log_form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                if user:
                    if not user.is_email_verified:
                        messages.error(request, 'Please verify your email before logging in. Check your inbox.')
                    else:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.name}! ✨')
                        return redirect(request.GET.get('next', 'feed'))
                else:
                    messages.error(request, 'Invalid email or password.')
            mode = 'login'

    return render(request, 'auth/auth.html', {
        'reg_form': reg_form,
        'log_form': log_form,
        'mode': mode,
    })


def register_view(request):
    return redirect('/auth/?mode=register')


def login_view(request):
    return redirect('/auth/?mode=login')


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon!")
    return redirect('auth')


def _send_verification_email(request, user, token_obj):
    """Helper: send verification email."""
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    verify_url = f'{protocol}://{domain}/verify-email/{token_obj.token}/'
    subject = 'Verify your PoetryHub account'
    html_message = render_to_string('auth/verify_email_body.html', {
        'user': user,
        'verify_url': verify_url,
    })
    send_mail(
        subject,
        f'Hi {user.name}, verify your email: {verify_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def verify_email_view(request, token):
    """Verify user email via token link."""
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        user = token_obj.user
        user.is_email_verified = True
        user.save()
        token_obj.delete()
        return render(request, 'auth/email_verified.html', {'user': user})
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'auth/email_verified.html', {'error': True})


def resend_verification_view(request):
    """Resend verification email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_email_verified:
                messages.info(request, 'This email is already verified. You can sign in.')
                return redirect('auth')
            token_obj, _ = EmailVerificationToken.objects.get_or_create(user=user)
            _send_verification_email(request, user, token_obj)
            return render(request, 'auth/email_verification_sent.html', {'email': email, 'resent': True})
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'auth/resend_verification.html')


def password_reset_request_view(request):
    """Request a password reset link."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            reset_url = f'{protocol}://{domain}/reset-password/{uid}/{token}/'
            subject = 'Reset your PoetryHub password'
            html_message = render_to_string('auth/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            send_mail(
                subject,
                f'Hi {user.name}, reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except CustomUser.DoesNotExist:
            pass  # Don't reveal whether email exists
        return render(request, 'auth/password_reset_done.html', {'email': email})
    return render(request, 'auth/password_reset.html')


def password_reset_confirm_view(request, uidb64, token):
    """Confirm password reset with new password."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            confirm = request.POST.get('confirm_password', '')
            if len(password) < 8:
                return render(request, 'auth/password_reset_confirm.html', {
                    'valid': True, 'error': 'Password must be at least 8 characters.'
                })
            if password != confirm:
                return render(request, 'auth/password_reset_confirm.html', {
                    'valid': True, 'error': 'Passwords do not match.'
                })
            user.set_password(password)
            user.save()
            return render(request, 'auth/password_reset_complete.html')
        return render(request, 'auth/password_reset_confirm.html', {'valid': True})
    else:
        return render(request, 'auth/password_reset_confirm.html', {'valid': False})


# ─── Feed & Poem Views ─────────────────────────────────────────────────────────

@login_required
def feed_view(request):
    genre_filter = request.GET.get('genre', '')
    search_query = request.GET.get('q', '')

    poems = Poem.objects.select_related('author').prefetch_related('likes', 'comments')

    if genre_filter:
        poems = poems.filter(genre=genre_filter)
    if search_query:
        poems = poems.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__name__icontains=search_query)
        )

    user_liked_ids = Like.objects.filter(user=request.user).values_list('poem_id', flat=True)

    # Unread DM count for navbar badge
    unread_dm = sum(
        c.unread_count(request.user)
        for c in request.user.conversations.all()
    )

    suggested_poets = CustomUser.objects.exclude(pk=request.user.pk)[:6]
    active_groups = ChatGroup.objects.all()[:4]

    return render(request, 'poems/feed.html', {
        'poems': poems,
        'genres': GENRE_CHOICES,
        'genre_filter': genre_filter,
        'search_query': search_query,
        'user_liked_ids': list(user_liked_ids),
        'unread_dm': unread_dm,
        'suggested_poets': suggested_poets,
        'active_groups': active_groups,
    })


@login_required
def ajax_comment_view(request, pk):
    if request.method == 'POST':
        poem = get_object_or_404(Poem, pk=pk)
        text = request.POST.get('text', '').strip()
        if text:
            c = Comment.objects.create(poem=poem, user=request.user, text=text)
            return JsonResponse({
                'success': True,
                'author': request.user.name,
                'author_initial': request.user.name[0].upper(),
                'text': c.text,
                'count': poem.comments.count(),
            })
    return JsonResponse({'error': 'Invalid'}, status=400)


@login_required
def poem_detail_view(request, pk):
    poem = get_object_or_404(Poem.objects.select_related('author'), pk=pk)
    comments = poem.comments.select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.poem = poem
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('poem_detail', pk=pk)

    user_liked = Like.objects.filter(user=request.user, poem=poem).exists()

    return render(request, 'poems/detail.html', {
        'poem': poem,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
    })


@login_required
def create_poem_view(request):
    form = PoemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        poem = form.save(commit=False)
        poem.author = request.user
        poem.save()
        messages.success(request, 'Your poem has been published! 🌟')
        return redirect('poem_detail', pk=poem.pk)
    return render(request, 'poems/create.html', {'form': form})


@login_required
def edit_poem_view(request, pk):
    poem = get_object_or_404(Poem, pk=pk, author=request.user)
    form = PoemForm(request.POST or None, instance=poem)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Poem updated successfully!')
        return redirect('poem_detail', pk=poem.pk)
    return render(request, 'poems/edit.html', {'form': form, 'poem': poem})


@login_required
def delete_poem_view(request, pk):
    poem = get_object_or_404(Poem, pk=pk, author=request.user)
    if request.method == 'POST':
        poem.delete()
        messages.success(request, 'Poem deleted.')
        return redirect('profile', username_id=request.user.pk)
    return render(request, 'poems/confirm_delete.html', {'poem': poem})


# ─── Like (AJAX) ──────────────────────────────────────────────────────────────

@login_required
def toggle_like_view(request, pk):
    if request.method == 'POST':
        poem = get_object_or_404(Poem, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, poem=poem)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'count': poem.like_count})
    return JsonResponse({'error': 'Invalid'}, status=400)


# ─── Profile Views ─────────────────────────────────────────────────────────────

@login_required
def profile_view(request, username_id):
    profile_user = get_object_or_404(CustomUser, pk=username_id)
    poems = Poem.objects.filter(author=profile_user).prefetch_related('likes', 'comments')
    user_liked_ids = Like.objects.filter(user=request.user).values_list('poem_id', flat=True)

    return render(request, 'poems/profile.html', {
        'profile_user': profile_user,
        'poems': poems,
        'user_liked_ids': list(user_liked_ids),
        'poem_count': poems.count(),
        'total_likes': sum(p.like_count for p in poems),
    })


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile', username_id=request.user.pk)
    return render(request, 'poems/edit_profile.html', {'form': form})


# ─── Direct Messages ───────────────────────────────────────────────────────────

@login_required
def inbox_view(request):
    """Shows all DM conversations + group chats."""
    conversations = request.user.conversations.prefetch_related('participants', 'messages')
    groups = request.user.chat_groups.all()

    # Unread count per conversation
    conv_data = []
    for conv in conversations:
        other = conv.other_user(request.user)
        last = conv.last_message()
        unread = conv.unread_count(request.user)
        conv_data.append({'conv': conv, 'other': other, 'last': last, 'unread': unread})

    group_data = []
    for grp in groups:
        last = grp.last_message()
        group_data.append({'group': grp, 'last': last})

    return render(request, 'messages/inbox.html', {
        'conv_data': conv_data,
        'group_data': group_data,
    })


@login_required
def start_dm_view(request, user_id):
    """Start or open DM with a user."""
    other = get_object_or_404(CustomUser, pk=user_id)
    if other == request.user:
        return redirect('inbox')

    # Find existing conversation
    conv = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)

    return redirect('dm_thread', conv_id=conv.pk)


@login_required
def dm_thread_view(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    if request.user not in conv.participants.all():
        return redirect('inbox')

    other = conv.other_user(request.user)
    msgs = conv.messages.select_related('sender')

    # Mark all as read
    msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    form = DirectMessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dm = form.save(commit=False)
        dm.conversation = conv
        dm.sender = request.user
        dm.save()
        # bump conversation updated_at
        conv.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': dm.pk,
                'content': dm.content,
                'sender_name': dm.sender.name,
                'sender_initial': dm.sender.name[0].upper(),
                'is_me': True,
                'time': dm.created_at.strftime('%H:%M'),
            })
        return redirect('dm_thread', conv_id=conv_id)

    return render(request, 'messages/dm_thread.html', {
        'conv': conv,
        'other': other,
        'msgs': msgs,
        'form': form,
    })


@login_required
def dm_poll_view(request, conv_id):
    """AJAX polling for new messages."""
    conv = get_object_or_404(Conversation, pk=conv_id)
    if request.user not in conv.participants.all():
        return JsonResponse({'error': 'Forbidden'}, status=403)
    last_id = int(request.GET.get('last_id', 0))
    new_msgs = conv.messages.filter(pk__gt=last_id).select_related('sender')
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    data = [{
        'id': m.pk,
        'content': m.content,
        'sender_name': m.sender.name,
        'sender_initial': m.sender.name[0].upper(),
        'is_me': m.sender == request.user,
        'time': m.created_at.strftime('%H:%M'),
    } for m in new_msgs]
    return JsonResponse({'messages': data})


# ─── Group Chats ───────────────────────────────────────────────────────────────

@login_required
def create_group_view(request):
    form = GroupCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        group = form.save(commit=False)
        group.admin = request.user
        group.save()
        group.members.add(request.user)
        # Add selected members
        for uid in request.POST.getlist('members'):
            try:
                u = CustomUser.objects.get(pk=uid)
                group.members.add(u)
            except CustomUser.DoesNotExist:
                pass
        messages.success(request, f'Group "{group.name}" created!')
        return redirect('group_chat', group_id=group.pk)
    all_users = CustomUser.objects.exclude(pk=request.user.pk)
    return render(request, 'messages/create_group.html', {'form': form, 'all_users': all_users})


@login_required
def group_chat_view(request, group_id):
    group = get_object_or_404(ChatGroup, pk=group_id)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('inbox')

    group_msgs = group.group_messages.select_related('sender')
    form = GroupMessageForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        gm = form.save(commit=False)
        gm.group = group
        gm.sender = request.user
        gm.save()
        group.save()  # bump updated_at
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': gm.pk,
                'content': gm.content,
                'sender_name': gm.sender.name,
                'sender_initial': gm.sender.name[0].upper(),
                'is_me': True,
                'time': gm.created_at.strftime('%H:%M'),
            })
        return redirect('group_chat', group_id=group_id)

    return render(request, 'messages/group_chat.html', {
        'group': group,
        'group_msgs': group_msgs,
        'form': form,
        'is_admin': group.admin == request.user,
    })


@login_required
def group_poll_view(request, group_id):
    """AJAX polling for new group messages."""
    group = get_object_or_404(ChatGroup, pk=group_id)
    if request.user not in group.members.all():
        return JsonResponse({'error': 'Forbidden'}, status=403)
    last_id = int(request.GET.get('last_id', 0))
    new_msgs = group.group_messages.filter(pk__gt=last_id).select_related('sender')
    data = [{
        'id': m.pk,
        'content': m.content,
        'sender_name': m.sender.name,
        'sender_initial': m.sender.name[0].upper(),
        'is_me': m.sender == request.user,
        'time': m.created_at.strftime('%H:%M'),
    } for m in new_msgs]
    return JsonResponse({'messages': data})


@login_required
def group_add_member_view(request, group_id):
    group = get_object_or_404(ChatGroup, pk=group_id, admin=request.user)
    if request.method == 'POST':
        uid = request.POST.get('user_id')
        try:
            u = CustomUser.objects.get(pk=uid)
            group.members.add(u)
            messages.success(request, f'{u.name} added to group!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect('group_chat', group_id=group_id)


@login_required
def group_leave_view(request, group_id):
    group = get_object_or_404(ChatGroup, pk=group_id)
    if request.method == 'POST':
        group.members.remove(request.user)
        messages.info(request, f'You left "{group.name}".')
        return redirect('inbox')
    return render(request, 'messages/leave_group.html', {'group': group})
