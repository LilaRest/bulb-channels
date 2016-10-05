from __future__ import unicode_literals

import importlib
import threading
from django.conf import settings

from .exceptions import DenyConnection
from .signals import consumer_started, consumer_finished, message_sent


class ConsumerMiddlewareRegistry(object):
    """
    Handles registration (via settings object) and generation of consumer
    middleware stacks
    """

    fixed_middleware = ["channels.consumer_middleware.ConvenienceMiddleware"]

    def __init__(self):
        # Load middleware callables from settings
        middleware_paths = self.fixed_middleware + getattr(settings, "CONSUMER_MIDDLEWARE", [])
        self.middleware_instances = []
        for path in middleware_paths:
            module_name, variable_name = path.rsplit(".", 1)
            try:
                self.middleware_instances.append(getattr(importlib.import_module(module_name), variable_name))
            except (ImportError, AttributeError) as e:
                raise ImproperlyConfigured("Cannot import consumer middleware %r: %s" % (path, e))

    def make_chain(self, consumer, kwargs):
        """
        Returns an instantiated chain of middleware around a final consumer.
        """
        next_layer = lambda message: consumer(message, **kwargs)
        for middleware_instance in reversed(self.middleware_instances):
            next_layer = middleware_instance(next_layer)
        return next_layer


class ConvenienceMiddleware(object):
    """
    Standard middleware which papers over some more explicit parts of ASGI.
    """

    runtime_data = threading.local()

    def __init__(self, consumer):
        self.consumer = consumer

    def __call__(self, message):
        print("conven", message.channel)
        if message.channel.name == "websocket.connect":
            # Websocket connect acceptance helper
            try:
                self.consumer(message)
                print ("messages sent", self.get_messages())
            except DenyConnection:
                message.reply_channel.send({"accept": False})
        else:
            # General path
            return self.consumer(message)

    @classmethod
    def reset_messages(cls, **kwargs):
        """
        Tied to the consumer started/ended signal to reset the messages list.
        """
        cls.runtime_data.sent_messages = []

    consumer_started.connect(lambda **kwargs: reset_messages())
    consumer_finished.connect(lambda **kwargs: reset_messages())

    @classmethod
    def sent_message(cls, channel, keys, **kwargs):
        """
        Called by message sending interfaces when messages are sent,
        for convenience errors only. Should not be relied upon to get
        all messages.
        """
        cls.runtime_data.sent_messages = getattr(cls.runtime_data, "sent_messages", []) + [(channel, keys)]
        print ("saved now", cls.runtime_data.sent_messages)

    message_sent.connect(lambda channel, keys, **kwargs: sent_message(channel, keys))

    @classmethod
    def get_messages(cls):
        return getattr(cls.runtime_data, "sent_messages", [])
