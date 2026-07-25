import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from app.config import get_settings
from app.database import async_session
from app.services.application_service import approve_application, decline_application

settings = get_settings()


def create_job_card(job: dict, score: float, app_id: int) -> str:
    """Create a formatted job card message."""
    portal_emoji = {
        "linkedin": "💼",
        "naukri": "🇮🇳",
        "wellfound": "🚀",
        "cutshort": "🎯",
        "iimjobs": "🎓",
        "hirect": "⚡",
        "foundit": "🔍",
        "indeed": "📋",
    }
    
    emoji = portal_emoji.get(job.get("portal", ""), "📌")
    remote_tag = "🌍 Remote" if job.get("is_remote") else "📍 " + (job.get("location") or "Not specified")
    
    salary = ""
    if job.get("salary_min") or job.get("salary_max"):
        min_sal = f"₹{job['salary_min']:,}" if job.get("salary_min") else "?"
        max_sal = f"₹{job['salary_max']:,}" if job.get("salary_max") else "?"
        salary = f"\n💰 {min_sal} - {max_sal}"
    
    return (
        f"{emoji} *{job.get('title', 'Unknown')}*\n"
        f"🏢 {job.get('company', 'Unknown Company')}\n"
        f"{remote_tag}\n"
        f"📊 Match Score: *{score:.0f}%*{salary}\n"
        f"🔗 {job.get('portal', '').title()}"
    )


def create_approval_keyboard(app_id: int, job_url: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for job approval."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Apply", callback_data=f"apply:{app_id}"),
            InlineKeyboardButton("❌ Skip", callback_data=f"skip:{app_id}"),
        ],
        [
            InlineKeyboardButton("👁 View JD", url=job_url),
        ],
    ])


def create_auto_apply_keyboard(app_id: int, job_url: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for auto-applied job confirmation."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirmed", callback_data=f"confirm:{app_id}"),
        ],
        [
            InlineKeyboardButton("👁 View JD", url=job_url),
        ],
    ])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🤖 *Job Automator Bot*\n\n"
        "I'll help you find and apply to Product Manager jobs in India.\n\n"
        "📌 *Commands:*\n"
        "/status - View application statistics\n"
        "/jobs - View recent job matches\n"
        "/help - Show this message\n\n"
        "I'll automatically search these portals every 4 hours:\n"
        "• LinkedIn • Naukri • Wellfound • Cutshort\n"
        "• iimjobs • Hirect • Foundit • Indeed\n\n"
        "Jobs with 90%+ match will be auto-applied.\n"
        "Other matches will be sent here for your approval.",
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show application stats."""
    from sqlalchemy import select, func
    from app.models.application import Application
    from app.models.job import Job

    async with async_session() as db:
        result = await db.execute(
            select(Application.status, func.count(Application.id)).group_by(Application.status)
        )
        stats = {row[0]: row[1] for row in result.all()}

        total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0

    await update.message.reply_text(
        "📊 *Application Statistics*\n\n"
        f"⏳ Discovered: {stats.get('discovered', 0)}\n"
        f"📝 To Apply: {stats.get('to_apply', 0)}\n"
        f"✅ Applied: {stats.get('applied', 0)}\n"
        f"📞 Screening: {stats.get('screening', 0)}\n"
        f"🎤 Interview: {stats.get('interview', 0)}\n"
        f"🎉 Completed: {stats.get('completed', 0)}\n\n"
        f"Total Jobs Scraped: {total_jobs}",
        parse_mode="Markdown"
    )


async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /jobs command - show recent matches."""
    from sqlalchemy import select
    from app.models.job import Job

    async with async_session() as db:
        result = await db.execute(
            select(Job).order_by(Job.match_score.desc().nullslast()).limit(5)
        )
        jobs = result.scalars().all()

    if not jobs:
        await update.message.reply_text(
            "📋 *Recent Job Matches*\n\nNo jobs scraped yet.",
            parse_mode="Markdown"
        )
        return

    lines = ["📋 *Top 5 Job Matches*\n"]
    for i, job in enumerate(jobs, 1):
        score = f"{job.match_score:.0f}%" if job.match_score else "N/A"
        lines.append(f"{i}. *{job.title}* @ {job.company}")
        lines.append(f"   📊 {score} | 📍 {job.location or 'Remote'}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await start_command(update, context)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()

    action, app_id = query.data.split(":")
    app_id = int(app_id)

    if action == "apply":
        async with async_session() as db:
            app = await approve_application(db, app_id)
            if app:
                await db.commit()
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "✅ *Application Approved!*\n\n"
            "Your application has been queued for submission.",
            parse_mode="Markdown"
        )

    elif action == "skip":
        async with async_session() as db:
            app = await decline_application(db, app_id)
            if app:
                await db.commit()
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "❌ *Job Skipped*\n\n"
            "This job has been marked as declined.",
            parse_mode="Markdown"
        )

    elif action == "confirm":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "✅ *Auto-Application Confirmed!*\n\n"
            "This job was auto-applied due to high match score.",
            parse_mode="Markdown"
        )


async def send_job_match(context: ContextTypes.DEFAULT_TYPE, job: dict, score: float, app_id: int):
    """Send a job match notification via Telegram job queue."""
    chat_id = context.job.data["chat_id"]

    message_text = create_job_card(job, score, app_id)

    if score >= settings.AUTO_APPLY_THRESHOLD:
        keyboard = create_auto_apply_keyboard(app_id, job.get("url", "#"))
        message_text += "\n\n🤖 *Auto-Applied (Score ≥ 90%)*"
    else:
        keyboard = create_approval_keyboard(app_id, job.get("url", "#"))

    await context.bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def send_notification_direct(chat_id: str, job: dict, score: float, app_id: int):
    """Send a notification directly using a Bot instance (for use from Celery workers)."""
    from telegram import Bot
    from app.config import get_settings

    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    message_text = create_job_card(job, score, app_id)

    if score >= settings.AUTO_APPLY_THRESHOLD:
        keyboard = create_auto_apply_keyboard(app_id, job.get("url", "#"))
        message_text += "\n\n🤖 *Auto-Applied (Score ≥ 90%)*"
    else:
        keyboard = create_approval_keyboard(app_id, job.get("url", "#"))

    await bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


def setup_bot() -> Application:
    """Set up and configure the Telegram bot."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("jobs", jobs_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    return application


if __name__ == "__main__":
    application = setup_bot()
    application.run_polling()
