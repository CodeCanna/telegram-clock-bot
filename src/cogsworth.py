from lib.Clock import Clock
from datetime import datetime, time, date, timedelta
from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application

import logging
import asyncio
import json
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def clock_in(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    date: datetime = datetime.now()
    clock: Clock = Clock(
        date.date(),
        date.time(),
        None,
        None,
        None,
        True,
        None
    )

    clock.save()
    print("Clocked In!")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Clocked in on {clock.date} at {clock.time_in}"
    )

async def take_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open('clock.json', 'r') as clock_file:
            clock = json.loads(clock_file.read())

            current_date: date = datetime.strptime(clock['date'], "%Y-%m-%d")
            time_in: time = datetime.strptime(clock['time_in'], "%H:%M:%S.%f")
            luch_time_start = datetime.now()

            clock: Clock = Clock(
                current_date.date(),
                time_in.time(),
                None,
                luch_time_start.time(),
                None,
                False,
                None
            )

            clock.save()
            print("Taking Lunch.")

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Taking lunch on {clock.date} at {clock.lunch_time_start}"
            )

    except IOError | FileNotFoundError as err:
        print(f"Couldn't go to lunch:{err}")

async def come_from_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open('clock.json', 'r') as clock_file:
            clock = json.loads(clock_file.read())

            current_date: date = datetime.strptime(clock['date'], "%Y-%m-%d")
            time_in: time = datetime.strptime(clock['time_in'], "%H:%M:%S.%f")
            lunch_time_start = datetime.strptime(clock['lunch_time_start'], "%H:%M:%S.%f")
            lunch_time_stop = datetime.now()

            clock: Clock = Clock(
                current_date.date(),
                time_in.time(),
                None,
                lunch_time_start.time(),
                lunch_time_stop.time(),
                True,
                None
            )

            clock.save()
            print("Lunch is over!")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Came back from lunch on {clock.date} at {clock.lunch_time_stop}"
            )
    except IOError | FileNotFoundError as err:
        print(f"Couldn't clock back in from lunch:{err}")

async def clock_out(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open('clock.json', 'r') as clock_file:
            clock = json.loads(clock_file.read())
            
            current_date: date = datetime.strptime(clock['date'], "%Y-%m-%d") # type: ignore
            time_in: datetime = datetime.strptime(clock['time_in'], "%H:%M:%S.%f") # type: ignore
            time_out: datetime = datetime.now()
            lunch_time_start = datetime.strptime(clock['lunch_time_start'], "%H:%M:%S.%f") if clock['lunch_time_start'] is not None else None
            lunch_time_stop = datetime.strptime(clock['lunch_time_stop'], "%H:%M:%S.%f") if clock['lunch_time_stop'] is not None else None

            clock: Clock = Clock(
                current_date.date(),
                time_in.time(),
                time_out.time(),
                lunch_time_start.time(),
                lunch_time_stop.time(),
                False,
                'Notes and shit!!!'
            )

            clock.save()
            print("Clocked Out!")
            print(clock.total_hours)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Clocked out on {clock.date} at {clock.time_out}"
            )
    except IOError | FileNotFoundError as err:
        print(f"Couldn't clock out: {err}")

def work(time_to_work: float):
    time.sleep(time_to_work)

def main() -> None:
    app: Application = ApplicationBuilder().token('974207105:AAFQIf5OrnhvmEVJxG2EbF0CbpR3E3lE9a0').build()
    handle_clockin = CommandHandler('in', clock_in)
    handle_clockout = CommandHandler('out', clock_out)
    handle_lunch_start = CommandHandler('lunch', take_lunch)
    handle_lunch_stop = CommandHandler('lunchstop', come_from_lunch)

    app.add_handler(handle_clockin)
    app.add_handler(handle_clockout)
    app.add_handler(handle_lunch_start)
    app.add_handler(handle_lunch_stop)

    app.run_polling()

if __name__ == '__main__':
    main()
"""
clock_in()
work(60)
take_lunch()
work(30) # Time to take lunch for
come_from_lunch()
work(60)
clock_out()
"""