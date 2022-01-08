#!/usr/bin/env python3

"""
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
"""

import sys
import requests
import platform
import subprocess
import json

from htmlwebshot import WebShot


#########################
### Telegram settings ###
CHAT_ID = ""
BOT_TOKEN = ""
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

### Templates ###########
MSG_TEMPLATE = f"""
*{platform.node()}:*
```
{{}}
```
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
  </head>
  <body>
    <pre>
{}
    </pre>
  </body>
</html>
"""
#########################


def get_attack_details(message):
    """Find attack details in logs and get data.

    Args:
        message (str): example - '192.0.2.0 incoming 2059522 attack_details'

    Returns:
        bool:
        str: output of last attack details
    """
    # get IP-address from message line
    ip = message.strip().split()[0]
    # get a file with attack details
    command = subprocess.run(
        f"ls -1t /var/log/fastnetmon_attacks/{ip}_*",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8")
    # check if command successfully executed
    if command.returncode != 0:
        return False, command.stderr

    # pick only last modified file
    command = command.stdout.strip().split()[0]
    with open(command) as file:
        data = file.read()
    return True, data


def create_image_attack_details(data):
    """Create images of attack_details.

    Args:
        data (str): the whole log of attack_details

    Returns:
        list: list of str, paths to images of attack_details
    """
    # crop useless data
    data = data.split('Flows have cropped due to very long list.')[1].strip()

    # settings for html to image convertor
    shot = WebShot()
    shot.params = {"--format": 'jpg'}

    # split data, cause it's too large
    paths_images_attack_details = []
    for count, s in enumerate(data.split("\n\n\n")):
        # create html from template
        html = HTML_TEMPLATE.format(s)
        # create image from html and save it in /tmp
        path = shot.create_pic(html=html, output=f"/tmp/fstm_attack_details_{str(count)}.jpg")
        paths_images_attack_details.append(path)
    return paths_images_attack_details


def send_message(text):
    """Send text via telegram.

    Args:
        text (str): your message
    """
    method = "/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "parse_mode": "markdown",
        'text': text
    }
    response = requests.post(API_URL + method, params)
    print(response.status_code)


def send_media(text, paths_images_attack_details):
    """Send images with caption via telegram.

    Args:
        text (str): your message
        paths_images_attack_details (list): list of str, that contain path to images in OS
    """
    method = "/sendMediaGroup"
    # create json for 'media' parameter and upload images
    images = []
    files = {}
    for count, s in enumerate(paths_images_attack_details):
        images.append(
            {
                "type": "photo",
                "caption": MSG_TEMPLATE.format(text) if count == 0 else '',
                "media": f"attach://{s.split('/')[-1]}",
                "parse_mode": "markdown"
            }
        )
        files[s.split('/')[-1]] = open(s, "rb")
    params = {
        'chat_id': CHAT_ID,
        'media': json.dumps(images)
    }
    response = requests.post(API_URL + method, params, files=files)
    print(response.status_code)


def main():
    # Get all passed arguments.
    message = " ".join(sys.argv[1:])

    # If message contain 'attack_details', send images.
    if 'attack_details' in message:
        status_get_attack_details, data = get_attack_details(message)
        if not status_get_attack_details:
            send_message(MSG_TEMPLATE.format(f"Can't get attack_details: {data}"))
        else:
            paths_images_attack_details = create_image_attack_details(data)
            send_media(message, paths_images_attack_details)
    else:
        send_message(MSG_TEMPLATE.format(message))


if __name__ == "__main__":
    main()
