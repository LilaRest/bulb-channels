Sessions
========

Channels supports standard Django sessions using HTTP cookies for both HTTP
and WebSocket. There are some caveats, however.


Basic Usage
-----------

The ``SessionMiddleware`` in Channels supports standard Django sessions,
and like all middleware, should be wrapped around the ASGI application that
needs the session information in its scope (for example, a ``URLRouter`` to
apply it to a whole collection of consumers, or an individual consumer).

``SessionMiddleware`` requires ``CookieMiddleware`` to function.
For convenience, these are also provided as a combined callable called
``SessionMiddlewareStack`` that includes both. All are importable from
``channels.session``.

To use the middleware, wrap it around the appropriate level of consumer
in your ``routing.py``::

    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.sessions import SessionMiddlewareStack

    from myapp import consumers

    application = ProtocolTypeRouter({

        "websocket": SessionMiddlewareStack(
            URLRouter([
                url(r"^front(end)/$", consumers.AsyncChatConsumer),
            ])
        ),

    })

``SessionMiddleware`` will only work on protocols that provide
HTTP headers in their ``scope`` - by default, this is HTTP and WebSocket.

To access the session, use ``self.scope["session"]`` in your consumer code::

    class ChatConsumer(WebsocketConsumer):

        def connect(self, event):
            self.scope["session"]["seed"] = random.randint(1, 1000)

``SessionMiddleware`` respects all the same Django settings as the default
Django session framework, like SESSION_COOKIE_NAME and SESSION_COOKIE_DOMAIN.


Session Persistence
-------------------

Within HTTP consumers or ASGI applications, session persistence works as you
would expect from Django HTTP views - sessions are saved whenever you send
a HTTP response that does not have status code ``500``.

This is done by overriding any ``http.response.start`` messages to inject
cookie headers into the response as you send it out. If you have set
the ``SESSION_SAVE_EVERY_REQUEST`` setting to ``True``, it will save the
session and send the cookie on every response, otherwise it will only save
whenever the session is modified.

If you are in a WebSocket consumer, however, the session is populated
**but will never be saved automatically** - you must call
``scope["session"].save()`` yourself whenever you want to persist a session
to your session store. If you don't save, the session will still work correctly
inside the consumer (as it's stored as an instance variable), but other
connections or HTTP views won't be able to see the changes.

.. note::

    If you are in a long-polling HTTP consumer, you might want to save changes
    to the session before you send a response. If you want to do this,
    call ``scope["session"].save()``.
