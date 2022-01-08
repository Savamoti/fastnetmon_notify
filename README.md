# fastnetmon_notify

## About

Just a notify script for [Fastnetmon](https://fastnetmon.com/), when fastnetmon takes any action, script sends messages to [Telegram](https://telegram.org/).


## Details

When the ban action occurs, fastnetmon sends two messages in a row to script's [stdin](https://fastnetmon.com/docs-fnm-advanced/notify-script-in-bash/), for example:

1. `192.0.2.0 incoming 2059522 ban`
2. `192.0.2.0 incoming 2059522 attack_details`

The second action is not processed in any way(in community edition) by fastnetmon, it just doesn't send the **attack_details**.

Script will find **attack_details** in the logs and send them as images, why image? cause details are enormous. It is not convenient to read large text in a telegram.


## Requirements

* `pip3 install htmlwebshot`
* `apt install wkhtmltopdf` # dependency for htmlwebshot


## How-to

Edit in script body a few variables:

* Telegram settings (CHAT_ID|BOT_TOKEN)
* Templates (MSG_TEMPLATE|HTML_TEMPLATE)
