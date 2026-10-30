# PoetryHub 📜✨

> A modern, full-stack poetry & community platform built with Python & Django.

## 🌟 Key Features

- 🎭 **Interactive Animated Split-Panel Auth** — Smooth sliding transition between Sign In & Registration with floating glowing orbs and frosted glassmorphism cards.
- 🔐 **Custom Authentication & Verification** — Secure credentials requiring **Email, Full Name, and Password** via a customized `AbstractBaseUser`. Includes **email verification tokens** on signup and resend verification handling.
- 🔑 **Forgot Password & Password Reset Flow** — Complete tokenized password recovery workflow with cryptographically secure, expiring reset links and custom-styled HTML transactional emails.
- 📸 **Instagram-Inspired UI Experience** — Left-docked navigation sidebar, active circles/poets stories tray, feed cards with instant reaction actions, and 3-column grid poet portfolio on profiles.
- 📝 **Poem Publishing & Rich Typography** — Publish poems with custom genres, preserving line breaks and styling with *Playfair Display* & *Inter*.
- ❤️ **Real-time AJAX Likes & Comments** — Instant like/unlike interactions with dynamic counter updates without full page reloads.
- 💬 **Direct Messaging (DMs)** — 1-on-1 private messaging between poets directly from their profile pages with live polling updates and unread message indicators.
- 👥 **Poetry Groups & Circles** — Create poetry clubs, add members, and collaborate in real-time group chat rooms.
- 🔍 **Search & Category Filtering** — Real-time keyword filtering across poem titles, content, and poets.
- 👤 **Poet Profiles** — Personal avatars, biographical details, poem portfolios, and cumulative like statistics.
- 🛡️ **Django Admin Dashboard** — Comprehensive management for users, posts, moderation, and messages at `/admin/`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Django 6.0 |
| **Database** | SQLite3 (configurable to PostgreSQL for production) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Vanilla JavaScript |
| **Design** | Glassmorphism, CSS Transitions, Responsive Grid |
| **Authentication** | Custom User Model (`AbstractBaseUser`) with email authentication |

---

## 🚀 Quickstart & Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Launch local development server
python manage.py runserver
```

Open your browser at **`http://127.0.0.1:8000/auth/`**

### 👥 Prebuilt Demo Accounts (for testing DMs, Feed, & Groups)

All prebuilt accounts have their password set to `password123` (Admin is `admin123`):

| Poet Name | Email | Password | Role / Details |
|---|---|---|---|
| **Admin Poet** | `admin@poetryhub.com` | `admin123` | Platform Admin, member of group |
| **Maya Lin** | `maya@poetryhub.com` | `password123` | Published 2 poems, active DMs |
| **Julian Brooks** | `julian@poetryhub.com` | `password123` | Published 1 poem, active DMs |
| **Aria Sterling** | `aria@poetryhub.com` | `password123` | Published 1 poem, active DMs |
| **Leo Vance** | `leo@poetryhub.com` | `password123` | Published 1 poem, member of group |

---

## 📄 Resume Project Highlight (Copy-Paste Ready)

> **PoetryHub — Full-Stack Social & Publishing Web Application**  
> *Technologies: Python, Django, JavaScript, SQLite/PostgreSQL, WhiteNoise, Bootstrap 5, HTML5/CSS3*
> - Engineered a full-stack social web app in Django enabling poets to publish creative works, engage in 1-on-1 direct messaging, and collaborate in group chat circles.
> - Implemented an interactive sliding glassmorphism authentication system supporting email verification tokens, secure password reset workflows, and custom user models (`AbstractBaseUser`).
> - Built an Instagram-inspired responsive UI with desktop sidebar navigation, stories tray, feed cards, and 3-column media grid layout.
> - Developed real-time asynchronous communication systems with AJAX polling for instant direct messages, group chats, and poem like/comment reactions.
> - Designed normalized relational database schemas (`CustomUser`, `Poem`, `Conversation`, `ChatGroup`, `DirectMessage`, `EmailVerificationToken`) with Django ORM, queries optimization, and admin moderation portal.
