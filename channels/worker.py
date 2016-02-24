from __future__ import unicode_literals

import logging
import time

from .exceptions import ConsumeLater
from .message import Message
from .utils import name_that_thing

logger = logging.getLogger('django.channels')


class Worker(object):
    """
    A "worker" process that continually looks for available messages to run
    and runs their consumers.
    """

    def __init__(self, channel_layer, callback=None):
        self.channel_layer = channel_layer
        self.callback = callback

    def run(self):
        """
        Tries to continually dispatch messages to consumers.
        """
        channels = self.channel_layer.registry.all_channel_names()
        while True:
            channel, content = self.channel_layer.receive_many(channels, block=True)
            # If no message, stall a little to avoid busy-looping then continue
            if channel is None:
                time.sleep(0.01)
                continue
            # Create message wrapper
            logger.debug("Worker got message on %s: repl %s", channel, content.get("reply_channel", "none"))
            message = Message(
                content=content,
                channel_name=channel,
                channel_layer=self.channel_layer,
            )
            # Handle the message
            consumer = self.channel_layer.registry.consumer_for_channel(channel)
            if self.callback:
                self.callback(channel, message)
            try:
                consumer(message)
            except ConsumeLater:
                self.channel_layer.send(channel, content)
            except:
                logger.exception("Error processing message with consumer %s:", name_that_thing(consumer))
