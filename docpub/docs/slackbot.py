from slacker import Slacker
from docpub.settings import DOCPUBENV, SLACK_TOKEN
import os


def slackbot(text):
    """
    Posts messages to Slack channel based on environment
    """

    slack = Slacker(SLACK_TOKEN)
    username = "DocPubBot"
    icon_url = "http://autobinaryrobots.com/wp-content/uploads/2016/11/robot.png"

    ## map environment to related Slack channel
    env_channels = {
        "local": "#docpublocal",
        "test": "#docpubtest",
        "prod": "#docpubprod"
    }
    
    ## set channel based on the environment
    channel = env_channels[DOCPUBENV]
    # channel = os.environ["MCCELECTIONSENV"]
    
    ## uses try statement in order to avoid requests package error:
        # "Max retries exceeded with url"
    try:
        slack.chat.post_message(channel, text, username=username, link_names=True, icon_url=icon_url)

        # return "Messaged posted: %s" % (text)
    
    except:
        print("WARNING: An error occured when trying to send the text to Slack.")

    ## outputs to command line so you can follow along/log there, especially when working locally
    print(text)
