# NotuBiz Calendar into Google Calendar
[NotuBiz](https://www.notubiz.nl/) is a Dutch council information system. 
This tool lets you automatically import the council calendar of a municipality into your Google Calendar.

The tool was created using [my unofficial NotuBiz Python client](https://github.com/RutgerRauws/python-notubiz).
I am not affiliated with NotuBiz in any way.

## Installation
First, create a new virtual environment, source into it, and install the dependencies.
```
python -m venv .venv
source .venv/bin/activate
pip install -r ./requirements.in
```

## Usage
To use this tool, you only need to modify the settings in `config.yaml`.

First, you need to find the ID of your Notubiz organisation. This ID can be found [here](https://api.notubiz.nl/organisations).
For example, the organisation ID of the municipality of Eindhoven is 686. 
Change the `organisation_id` value in the config file accordingly.

The tool imports a user-definable number of weeks ahead. You can change `weeks_ahead` if you desire, but I recommend starting with 12 weeks.

In order to import the Notubiz calendar items into Google Calendar, we need to authenthicate our 'app' and get access to the Google API. Read [this article](https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html) on how to create your own `credentials.json` and store them in the folder `.credentials`.

Now, set the `google_mail_address` in `config.yaml` to the e-mail address of your Google Account used in the step before.

Lastly, go to [calendar.google.com](https://calendar.google.com) and create a new calendar that you wish to let this tool use.
After creating this calendar, go to the calendar's settings to look up the Calendar ID and copy paste this value in  `google_calendar_id` of `config.yaml`. This value should have a format like: `xxxxxxxxxxx@group.calendar.google.com`

That's it! Now run the script and within a few seconds (depending on how many weeks you have selected and how full the Notubiz calendar is) the import should be complete! You could run this script as a cronjob, for instance.