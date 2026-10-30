import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poetryhub.settings')
django.setup()

from poems.models import CustomUser, Poem, Like, Comment, Conversation, DirectMessage, ChatGroup, GroupMessage

def seed():
    print("🌱 Starting database seeding...")

    # 1. Create or get Admin
    admin, _ = CustomUser.objects.get_or_create(
        email='admin@poetryhub.com',
        defaults={'name': 'Admin Poet', 'bio': 'Curator & custodian of PoetryHub 📜'}
    )
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_email_verified = True
    admin.save()

    # 2. Prebuilt Poets
    users_data = [
        {
            'email': 'maya@poetryhub.com',
            'name': 'Maya Lin',
            'bio': 'Words are quiet storms. Writing contemporary prose, haikus, and free verse. Coffee enthusiast ☕',
            'password': 'password123',
        },
        {
            'email': 'julian@poetryhub.com',
            'name': 'Julian Brooks',
            'bio': 'Romantic classicist wandering through misty coastlines and autumn forests 🌲📜',
            'password': 'password123',
        },
        {
            'email': 'aria@poetryhub.com',
            'name': 'Aria Sterling',
            'bio': 'Chasing neon dawns and forgotten constellations. Spoken word artist & dream architect ✨',
            'password': 'password123',
        },
        {
            'email': 'leo@poetryhub.com',
            'name': 'Leo Vance',
            'bio': 'Exploring existential reflections and philosophical rhythm in every verse.',
            'password': 'password123',
        },
    ]

    poets = {}
    poets['admin'] = admin

    for udata in users_data:
        u, created = CustomUser.objects.get_or_create(
            email=udata['email'],
            defaults={'name': udata['name'], 'bio': udata['bio']}
        )
        u.set_password(udata['password'])
        u.is_email_verified = True
        u.save()
        poets[udata['email'].split('@')[0]] = u
        print(f"  ✓ User ready: {u.name} ({u.email})")

    # 3. Create Sample Poems
    poems_data = [
        {
            'author': poets['maya'],
            'title': 'Whispers of Rain',
            'genre': 'nature',
            'content': """The clouds descend in velvet gray,
To wash the crowded streets of day.
Each droplet sounds a crystal chime,
A tender pulse untouched by time.

Against the window pane they cling,
Like silent notes the shadows sing,
And in the quiet dark retreat,
The earth awakens at my feet."""
        },
        {
            'author': poets['julian'],
            'title': 'Echoes of a Forgotten Harbor',
            'genre': 'life',
            'content': """Salt on the timber, rust on the chain,
A lantern flickers through drifting rain.
The ships have sailed to distant shores,
Leaving behind the weathered oars.

We build our hopes upon the sea,
And wonder what was meant to be,
While tides return and gently tell:
All things that wander, sleep as well."""
        },
        {
            'author': poets['aria'],
            'title': 'Starlight in Neon Cities',
            'genre': 'hope',
            'content': """Above the hum of midnight traffic lights,
A million constellations stake their claim,
Through smog and glass and artificial nights,
They whisper every dreamer by their name.

Do not surrender to the concrete floor,
When galaxies are knocking at your door."""
        },
        {
            'author': poets['leo'],
            'title': 'The Architecture of Silence',
            'genre': 'spiritual',
            'content': """Before the syllable took flight,
Before the candle learned the light,
There was a chamber deep and vast,
Where no shadow could be cast.

In listening, the truth is found,
Not in the fury of the sound,
But in the pause between two breaths,
Where life outlasts a thousand deaths."""
        },
        {
            'author': poets['maya'],
            'title': 'Paper Cranes and Old Letters',
            'genre': 'love',
            'content': """I folded each promise into wings of white,
And set them adrift on the breeze tonight.
If distance is measured by words left unsaid,
Then oceans are shallow where lovers have bled.

Return with the morning, or linger in skies,
For love is the truth that outlives goodbyes."""
        },
    ]

    created_poems = []
    for pdata in poems_data:
        p, created = Poem.objects.get_or_create(
            title=pdata['title'],
            author=pdata['author'],
            defaults={
                'content': pdata['content'],
                'genre': pdata['genre'],
            }
        )
        created_poems.append(p)
        print(f"  ✓ Poem ready: '{p.title}' by {p.author.name}")

    # 4. Likes & Comments
    sample_comments = [
        (poets['julian'], created_poems[0], "The rhythm in the third stanza is mesmerizing, Maya."),
        (poets['aria'], created_poems[0], "I felt this in my soul. Rainy nights inspire the deepest verses."),
        (poets['maya'], created_poems[1], "Haunting imagery Julian. 'All things that wander, sleep as well' is pure gold."),
        (admin, created_poems[2], "Stunning juxtaposition of modern cityscapes and cosmos, Aria!"),
        (poets['leo'], created_poems[3], "Pondering the spaces between our thoughts... beautifully executed."),
    ]

    for user, poem, text in sample_comments:
        Comment.objects.get_or_create(user=user, poem=poem, text=text)
        Like.objects.get_or_create(user=user, poem=poem)

    # Cross likes
    for p in created_poems:
        for u in poets.values():
            if u != p.author:
                Like.objects.get_or_create(user=u, poem=p)

    print("  ✓ Likes and comments populated.")

    # 5. Direct Message Conversations with Admin
    # Reset existing to prevent duplicates
    Conversation.objects.all().delete()
    DirectMessage.objects.all().delete()

    # DM between Admin & Maya Lin
    conv1 = Conversation.objects.create()
    conv1.participants.set([admin, poets['maya']])
    conv1_msgs = [
        (poets['maya'], "Hi! Welcome to PoetryHub. I loved reading through the new collections!"),
        (admin, "Thank you Maya! Your poem 'Whispers of Rain' set such a wonderful tone for the platform."),
        (poets['maya'], "That means so much! I'm working on a sonnet collection next. Would love to get your feedback soon!"),
    ]
    for sender, content in conv1_msgs:
        DirectMessage.objects.create(conversation=conv1, sender=sender, content=content)

    # DM between Admin & Julian Brooks
    conv2 = Conversation.objects.create()
    conv2.participants.set([admin, poets['julian']])
    conv2_msgs = [
        (poets['julian'], "Greetings! Just dropped my latest piece 'Echoes of a Forgotten Harbor'."),
        (admin, "Checking it out now Julian, love the maritime theme."),
        (poets['julian'], "Much appreciated! Let me know if you want to collaborate on the weekend prompt."),
    ]
    for sender, content in conv2_msgs:
        DirectMessage.objects.create(conversation=conv2, sender=sender, content=content)

    # DM between Maya & Aria
    conv3 = Conversation.objects.create()
    conv3.participants.set([poets['maya'], poets['aria']])
    conv3_msgs = [
        (poets['aria'], "Maya! Loved your paper cranes poem so much."),
        (poets['maya'], "Aria!! Thank you so much, your city lights piece gave me chills."),
    ]
    for sender, content in conv3_msgs:
        DirectMessage.objects.create(conversation=conv3, sender=sender, content=content)

    print("  ✓ Direct Message conversations created.")

    # 6. Prebuilt Group: The Midnight Sonnets Society
    group, _ = ChatGroup.objects.get_or_create(
        name="The Midnight Sonnets Society",
        defaults={
            'description': "A circle for midnight thinkers, sonneteers, and free verse adventurers.",
            'admin': admin
        }
    )
    group.members.set([admin, poets['maya'], poets['julian'], poets['aria'], poets['leo']])

    group_messages = [
        (admin, "Welcome to The Midnight Sonnets Society, everyone! 🌟"),
        (poets['maya'], "So thrilled to be here! What is our first weekly theme?"),
        (poets['julian'], "I propose 'Solitude and Sea Mist'."),
        (poets['aria'], "I love that! Or maybe 'Echoes in the Dark'."),
        (poets['leo'], "Both can weave together beautifully. Excited to read everyone's drafts tonight."),
    ]

    for sender, content in group_messages:
        GroupMessage.objects.get_or_create(group=group, sender=sender, content=content)

    print("  ✓ Group 'The Midnight Sonnets Society' populated.")
    print("✨ Seeding successfully completed!")

if __name__ == '__main__':
    seed()
