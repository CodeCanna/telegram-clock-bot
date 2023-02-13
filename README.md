# telegram-clock-bot
A simple bot to track my time at work.

# How to use
Clone the project in the directory you want it to live, paste in your Telegram API key you got from BotFather into
the secret_sauce.json file where it says `YOUR_API_KEY_HERE`; keep the double quotes.

`cd` into the directory you just cloned.
Run `python src/cogsworth.py`, or on Windows `python src\cogsworth.py` and start your bot from the telegram app using `/start`.

# Available Commands
* `/in` - Clocks you in
* `/out` - Clocks you out and calucates your time with or without taking a lunch
* `/lunch` - Clocks you out for lunch
* `/lunchstop` - Clocks you back in from lunch and records your lunch times

## NOTE
Telegram BotFather allows you to define quick command buttons so you don't have to physically type in these commands everytime.
Go the the BotFather and type `/mybots`, select your bot and hit the `Edit Bot` button, then hit `Edit Commands` and follow
the BotFather's prompts to add the above commands to your bot. When sending them to the bot father leave off the `/`.

### Example 
When bot father asks you to give a list of commands give them in this format
* `in - Clock me in`
* `out - Clock me out`
* `lunch - Start lunch`
* `lunchstop - End Lunch`
