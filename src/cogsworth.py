from lib.Clock import Clock
from datetime import datetime, time, date, timedelta
from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application

import logging
import asyncio
import json
import time

"""
cogsworth.py is the actual script ran by the telegram bot.  It works by creating instances of Clock based on the current clock.json
state and re-saving over the old clock.json state.

The clock.json file is only used to keep state and is cleared after clocking out for the day.  A CSV is generated with the
data generated from use throughout the day and the clock.json file is "reset".
"""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load and read the secret sauce I.E. API key
def secret_sauce(saucy_file: str) -> dict:
    with open(saucy_file, 'r') as sauce:
        ss: dict = json.loads(sauce.read())
        return ss

async def clock_in(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # If clock.json is not found
        if not Clock.clockfile_detected():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"clock.json not found.  Attempting to create..."
            )

            # Create clock.json file
            Clock.create_clockfile()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Successfully created clock.json try clocking in again."
            )

            # Return to allow the user to try clocking in again.
            return
        elif Clock.clocked_in('clock.json'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"You are already clocked in!"
            )

            # Return without doing anything because I'm already clocked in.
            return
        elif Clock.dict_from_file('clock.json')['lunch_time_start'] and Clock.dict_from_file('clock.json')['lunch_time_stop'] is None and Clock.dict_from_file('clock.json')['is_clocked_in'] is False:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are at lunch, can't clock you in without ending your lunch."
            )

            # Return without clocking me in because I'm at lunch.
            return

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
    except IOError or FileNotFoundError as err:
        print(f"Couldn't clock you in: {err}")
        try:
            print("Attempting to create clock.json.")
            with open('clock.json', 'w') as clock_file:
                print("clock.json file created please try clocking in again.")
        except IOError as err:
            print(f"Failed creating clock.json: {err}")


async def take_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if Clock.at_lunch('clock.json'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Already at lunch!"
            )
            return
        elif Clock.clock_cleared():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Can't go to lunch if you haven't clocked in!"
            )
            return
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

    except IOError or FileNotFoundError as err:
        print(f"Couldn't go to lunch:{err}")

async def come_from_lunch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not Clock.at_lunch('clock.json'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You aren't at lunch."
            )

            return
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
    except IOError or FileNotFoundError as err:
        print(f"Couldn't clock back in from lunch:{err}")

async def clock_out(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not Clock.clocked_in('clock.json'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Already clocked out!"
            )

            return
        with open('clock.json', 'r') as clock_file:
            clock = json.loads(clock_file.read())
            
            current_date: date = datetime.strptime(clock['date'], "%Y-%m-%d") # type: ignore
            time_in: datetime = datetime.strptime(clock['time_in'], "%H:%M:%S.%f") # type: ignore
            time_out: datetime = datetime.now()
            lunch_time_start_dt = datetime.strptime(clock['lunch_time_start'], "%H:%M:%S.%f") if clock['lunch_time_start'] is not None else None
            lunch_time_stop_dt = datetime.strptime(clock['lunch_time_stop'], "%H:%M:%S.%f") if clock['lunch_time_stop'] is not None else None

            lunch_time_start = lunch_time_start_dt.time() if lunch_time_start_dt is not None else None
            lunch_time_stop = lunch_time_stop_dt.time() if lunch_time_stop_dt is not None else None

            clock: Clock = Clock(
                current_date.date(),
                time_in.time(),
                time_out.time(),
                lunch_time_start,
                lunch_time_stop,
                False,
                'Notes and shit!!!'
            )

            clock.save()
            print("Clocked Out!")
            print(clock.total_hours)

            # Generate a CSV representation of our Clock object
            clock.export_csv()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Clocked out on {clock.date} at {clock.time_out}.\nYou clocked {clock.total_hours}."
            )

            # Send our generated CSV to the user
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f"{clock.date}.csv",
                caption=f"{clock.date} CSV File"
            )

            # Clear the clock.json file to reuse.
            clock.clear_clock()
    except IOError as err:
        print(f"Couldn't clock out: {err}")

def main(ss: dict) -> None:
    app: Application = ApplicationBuilder().token(ss['BOT_KEY']).build()

    # Define our bot options
    handle_clockin = CommandHandler('in', clock_in)
    handle_clockout = CommandHandler('out', clock_out)
    handle_lunch_start = CommandHandler('lunch', take_lunch)
    handle_lunch_stop = CommandHandler('lunchstop', come_from_lunch)

    # Add our handlers for each option
    app.add_handler(handle_clockin)
    app.add_handler(handle_clockout)
    app.add_handler(handle_lunch_start)
    app.add_handler(handle_lunch_stop)

    app.run_polling()

if __name__ == '__main__':
    ss = secret_sauce('secret_sauce.json')
    main(ss)