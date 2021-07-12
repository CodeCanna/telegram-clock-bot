import telegram
import sys
from telegram.ext import Updater, CommandHandler

import datetime
import json
import logging

def main(ss: object) -> None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    derg_updater = Updater(token=ss['BOT_KEY'], use_context=True)
    dispatcher = derg_updater.dispatcher
    # Create my handlers
    start_handler = CommandHandler('start', start)
    say_hi_handler = CommandHandler('hello', hello)
    clock_in_handler = CommandHandler('clock_in', clock_in)
    clock_out_handler = CommandHandler('clock_out', clock_out)
    add_research_note_handler = CommandHandler('note', add_research_note)
    # Register them with the dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(say_hi_handler)
    dispatcher.add_handler(clock_in_handler)
    dispatcher.add_handler(clock_out_handler)
    dispatcher.add_handler(add_research_note_handler)
    derg_updater.start_polling()

# Load Secret Sauce shall we?

"""
Loads the secret sauce.
"""
def lss(sauce_path: sys.path) -> object:
    secret_dict = {}
    try:
        # Load the secret sauce
        secret_sauce = open(sauce_path)
        secret_dict = json.load(secret_sauce)
    except FileNotFoundError:
        # End if the secret sauce isn't found
        print("The secret sauce wasn't found, exitting...")
        exit(1)
    return secret_dict

# Say hello to the user if they please


def hello(update, context):
    hello_str = "Hello " + update.message.from_user['username'] + "!"
    context.bot.send_message(chat_id=ss['CHAT_ID'], text=hello_str)

# Start EX Command


def start(update, context):
    kb = [[telegram.KeyboardButton('/clock_in')], [telegram.KeyboardButton('/Break')], [
        telegram.KeyboardButton('/clock_out')]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb)
    context.bot.send_message(
        chat_id=ss['CHAT_ID'], text="Press Button", reply_markup=kb_markup)

"""
Create a fresh python representation of clock_cfg.json
"""
def initialize_clock_obj() -> object:
    clock_obj = {
        "date_today": "",
        "clock_in_time": "",
        "lunch": {
            "lunch_start_time": "",
            "lunch_end_time": "",
            "lunch_total_time": None
        },
        "clock_out_time": "",
        "research_notes": [],
        "is_clocked_in": False,
        "today_total_hours": None
    }
    return clock_obj


"""
This sets is_clocked_in to false and calculates my time on the clock, the bot outputs the time in the clock group
"""
def clock_out(update, context) -> None:
    try:
        cl_obj = json.load(open("./clock_cfg.json"))
        cl_in_time = cl_obj['clock_in_time']
        cl_today = cl_obj['date_today']
        if cl_obj['is_clocked_in'] == True:
            cl_obj = initialize_clock_obj()
            cl_obj['clock_in_time'] = cl_in_time
            cl_obj['clock_out_time'] = str(datetime.datetime.now().time().strftime('%I:%M:%S %p'))
            cl_obj['date_today'] = cl_today
            # Calculate our time
            start_time = datetime.datetime.strptime(cl_obj['clock_in_time'], '%I:%M:%S %p')
            end_time = datetime.datetime.strptime(cl_obj['clock_out_time'], '%I:%M:%S %p')
            cl_obj['today_total_hours'] = str(abs((start_time - end_time)))
            # Send a response with the calculated hours
            response = "You clocked out at " + str(end_time.strftime('%I:%M:%S %p')) + ".  " + "You got " + str(cl_obj['today_total_hours']) + " today."
            context.bot.send_message(chat_id=ss["CHAT_ID"], text=response)
            json.dump(cl_obj, open('./clock_cfg.json', 'w'))
        else:
            print("You are already clocked out.")
            context.bot.send_message(chat_id=ss['CHAT_ID'], text="You are already clocked out!")
    except FileNotFoundError:
        print("Clock file clock_cfg.json not found...")
        
"""
This clocks us in, by setting the is_clocked_in field in the clock_cfg.json file to true, and setting a time for clock_in_time
"""
def clock_in(update, context) -> None:
    try:
        # First check that we are NOT already clocked in
        if not json.loads(get_json("./clock_cfg.json"))["is_clocked_in"]:
            # This sets the initial is_clocked_in to false each run
            cl_obj = initialize_clock_obj()
            cl_obj['date_today'] = str(datetime.datetime.now().date())
            cl_obj['clock_in_time'] = str(datetime.datetime.now().time().strftime('%I:%M:%S %p'))
            cl_obj['is_clocked_in'] = True
            cl_file = open("./clock_cfg.json", 'w')
            response = "You clocked in at " + str(cl_obj['clock_in_time'])
            context.bot.send_message(chat_id=ss['CHAT_ID'], text=response)
            # Write new data to json file
            json.dump(cl_obj, cl_file)
            cl_file.close()
        else:
            print("Already clocked in!")
            context.bot.send_message(chat_id=ss['CHAT_ID'], text="You are already clocked out!")
    except FileNotFoundError:
        print("Clock file clock_cfg.json not found...")

"""
This returns the JSON as str from clock_cfg.json to be used
"""
def get_json(file: sys.path) -> str:
    file_obj = open(file, 'r')
    file_contents = file_obj.read()
    file_obj.close()
    return file_contents

"""
Function to add a reasearch note to the day...not working yet
"""
def add_research_note(update, context):
    # Load today's clock info

    cl_obj = get_json("./clock_cfg.json")
    cl_dict = json.loads(cl_obj)

    for note in context.args:
        cl_dict['research_notes'].append(note)

    cl_file = open("./clock_cfg.json", "w")
    json.dump(cl_dict, cl_file)
    cl_file.close()


if __name__ == "__main__":
    ss = lss("./secret_sauce.json")
    main(ss)