# Job Automator - Product Manager Jobs India

Automated job search and application tracking system for Product Manager roles in India.

## Features

- **Multi-Portal Scraping**: LinkedIn, Naukri, Wellfound, Cutshort, iimjobs, Hirect, Foundit, Indeed
- **Smart Matching**: TF-IDF + skill-based matching engine (0-100 score)
- **Auto-Apply**: Automatically applies to jobs with 90%+ match score
- **Telegram Integration**: Get job matches and approve/skip via Telegram bot
- **Location Filtering**: Hyderabad for in-person/hybrid, anywhere in India for remote
- **Dashboard**: Kanban board tracking: Discovered → To Apply → Applied → Screening → Interview → Completed

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python/FastAPI + Celery |
| Frontend | Next.js + Tailwind CSS |
| Database | PostgreSQL (Neon free tier) |
| Queue | Redis (Upstash free tier) |
| Messaging | Telegram Bot API |
| Scraping | Playwright |
| Hosting | Render (backend) + Vercel (frontend) |

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd job-automator

# Backend setup
cd backend
cp .env.example .env
# Edit .env with your Telegram bot token

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 2. Start Services

```bash
# From project root
docker-compose up -d

# Or run locally:
# Terminal 1: PostgreSQL + Redis (or use docker)
docker-compose up postgres redis

# Terminal 2: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 3: Celery Worker
celery -A app.workers.celery_app:celery_app worker -l info

# Terminal 4: Celery Beat (scheduler)
celery -A app.workers.celery_app:celery_app beat -l info

# Terminal 5: Frontend
cd frontend
npm run dev
```

### 3. Configure Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token to `backend/.env` as `TELEGRAM_BOT_TOKEN`
4. Start your bot and note your chat ID

### 4. Access

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Telegram Bot**: Start a chat with your bot

## Project Structure

```
job-automator/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── bot/           # Telegram bot
│   │   ├── matching/      # TF-IDF matching engine
│   │   ├── models/        # SQLAlchemy models
│   │   ├── scrapers/      # Portal scrapers
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── workers/       # Celery tasks
│   └── alembic/           # DB migrations
├── frontend/
│   └── src/
│       ├── app/           # Next.js pages
│       ├── components/    # React components
│       └── lib/           # API client
└── docker-compose.yml
```

## Kanban Board Columns

| Column | Description |
|--------|-------------|
| Discovered | New jobs scraped, awaiting review |
| To Apply | Approved (manual or auto), queued for submission |
| Applied | Application sent to portal |
| Screening | Company reviewing your application |
| Interview | Interview scheduled/in progress |
| Completed | Offer received OR rejected/withdrawn |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Dashboard statistics |
| GET | `/api/v1/jobs` | List jobs (filterable) |
| GET | `/api/v1/applications` | List applications |
| POST | `/api/v1/applications/{id}/approve` | Approve application |
| POST | `/api/v1/applications/{id}/decline` | Decline application |
| GET | `/api/v1/profile` | Get user profile |
| PUT | `/api/v1/profile` | Update profile |

## Free Infrastructure

| Service | Free Tier |
|---------|-----------|
| Render | 750 hrs/mo (backend) |
| Vercel | Unlimited (frontend) |
| Neon | 0.5 GB PostgreSQL |
| Upstash | 10K Redis commands/day |
| Telegram Bot API | Free |

## Environment Variables

See `backend/.env.example` for all required variables.

## License

MIT
