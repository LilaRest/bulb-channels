from __future__ import unicode_literals

import fnmatch
import re

import django
from django.conf import settings
from django.utils.module_loading import import_string

from .exceptions import InvalidChannelLayerError
from .utils import name_that_thing


class ChannelLayerManager:
    """
    Takes a settings dictionary of backends and initialises them on request.
    """

    def __init__(self):
        self.backends = {}

    @property
    def configs(self):
        # Lazy load settings so we can be imported
        return getattr(settings, "CHANNEL_LAYERS", {})

    def make_backend(self, name):
        """
        Instantiate channel layer.
        """
        config = self.configs[name].get("CONFIG", {})
        return self._make_backend(name, config)

    def make_test_backend(self, name):
        """
        Instantiate channel layer using its test config.
        """
        try:
            config = self.configs[name]["TEST_CONFIG"]
        except KeyError:
            raise InvalidChannelLayerError("No TEST_CONFIG specified for %s" % name)
        return self._make_backend(name, config)

    def _make_backend(self, name, config):
        # Check for old format config
        if "ROUTING" in self.configs[name]:
            raise InvalidChannelLayerError("ROUTING key found for %s - this is no longer needed in Channels 2." % name)
        # Load the backend class
        try:
            backend_class = import_string(self.configs[name]["BACKEND"])
        except KeyError:
            raise InvalidChannelLayerError("No BACKEND specified for %s" % name)
        except ImportError:
            raise InvalidChannelLayerError(
                "Cannot import BACKEND %r specified for %s" % (self.configs[name]['BACKEND'], name)
            )
        # Initialise and pass config
        return backend_class(**config)

    def __getitem__(self, key):
        if key not in self.backends:
            self.backends[key] = self.make_backend(key)
        return self.backends[key]

    def __contains__(self, key):
        return key in self.configs

    def set(self, key, layer):
        """
        Sets an alias to point to a new ChannelLayerWrapper instance, and
        returns the old one that it replaced. Useful for swapping out the
        backend during tests.
        """
        old = self.backends.get(key, None)
        self.backends[key] = layer
        return old


class BaseChannelLayer:
    """
    Base channel layer class that others can inherit from, with useful
    common functionality.
    """

    def compile_capacities(self, channel_capacity):
        """
        Takes an input channel_capacity dict and returns the compiled list
        of regexes that get_capacity will look for as self.channel_capacity/
        """
        result = []
        for pattern, value in channel_capacity.items():
            # If they passed in a precompiled regex, leave it, else intepret
            # it as a glob.
            if hasattr(pattern, "match"):
                result.append((pattern, value))
            else:
                result.append((re.compile(fnmatch.translate(pattern)), value))
        return result

    def get_capacity(self, channel):
        """
        Gets the correct capacity for the given channel; either the default,
        or a matching result from channel_capacity. Returns the first matching
        result; if you want to control the order of matches, use an ordered dict
        as input.
        """
        for pattern, capacity in self.channel_capacity:
            if pattern.match(channel):
                return capacity
        return self.capacity

    def match_type_and_length(self, name):
        if (len(name) < 100) and isinstance(name, str):
            return True
        return False

    ### Name validation functions

    channel_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+(\![\d\w\-_.]*)?$")
    group_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+$")
    invalid_name_error = "{} name must be a valid unicode string containing only ASCII alphanumerics, hyphens, underscores, or periods."

    def valid_channel_name(self, name, receive=False):
        if self.match_type_and_length(name):
            if bool(self.channel_name_regex.match(name)):
                # Check cases for special channels
                if "!" in name and not name.endswith("!") and receive:
                    raise TypeError("Specific channel names in receive() must end at the !")
                return True
        raise TypeError("Channel name must be a valid unicode string containing only ASCII alphanumerics, hyphens, or periods, not '{}'.".format(name))

    def valid_group_name(self, name):
        if self.match_type_and_length(name):
            if bool(self.group_name_regex.match(name)):
                return True
        raise TypeError("Group name must be a valid unicode string containing only ASCII alphanumerics, hyphens, or periods.")

    def valid_channel_names(self, names, receive=False):
        _non_empty_list = True if names else False
        _names_type = isinstance(names, list)
        assert _non_empty_list and _names_type, "names must be a non-empty list"

        assert all(self.valid_channel_name(channel, receive=receive) for channel in names)
        return True

    def non_local_name(self, name):
        """
        Given a channel name, returns the "non-local" part. If the channel name
        is a process-specific channel (contains !) this means the part up to
        and including the !; if it is anything else, this means the full name.
        """
        if "!" in name:
            return name[:name.find("!")+1]
        else:
            return name



def get_channel_layer(alias="default"):
    """
    Returns a channel layer by alias.
    """
    return channel_layers[alias]


# Default global instance of the channel layer manager
channel_layers = ChannelLayerManager()
