Django Channels
===============

.. image:: https://api.travis-ci.org/andrewgodwin/channels.svg
    :target: https://travis-ci.org/andrewgodwin/channels

.. image:: https://img.shields.io/pypi/dm/channels.svg
    :target: https://pypi.python.org/pypi/channels
    
.. image:: https://readthedocs.org/projects/channels/badge/?version=latest
    :target: http://channels.readthedocs.org/en/latest/?badge=latest
    
.. image:: https://img.shields.io/pypi/v/channels.svg
    :target: https://pypi.python.org/pypi/channels

.. image:: https://img.shields.io/pypi/l/channels.svg
    :target: https://pypi.python.org/pypi/channels

*(Note: Recent versions of Channels also need recent versions of Daphne,
asgi_redis and asgiref, so make sure you update all at once)*

This is a work-in-progress code branch of Django implemented as a third-party
app, which aims to bring some asynchrony to Django and expand the options
for code beyond the request-response model, in particular enabling WebSocket,
HTTP2 push, and background task support.

This is still **beta** software: the API is mostly settled, but might change
a bit as things develop.

Documentation, installation and getting started instructions are at
http://channels.readthedocs.org

You can also install channels from PyPI as the ``channels`` package.
You'll likely also want ``asgi_redis`` to provide the Redis channel layer.
