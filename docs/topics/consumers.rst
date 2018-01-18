Consumers
=========

While Channels is built around a basic low-level spec called
:doc:`ASGI </asgi>`, it's more designed for interoperability than for writing
complex applications in. So, Channels provides you with Consumers, a rich
abstraction that allows you to make ASGI applications easily.

Consumers do a couple of things in particular:

* Structures your code as a series of functions to be called whenever an
  event happens, rather than making you write an event loop.

* Allow you to write synchronous or async code and deals with handoffs
  and threading for you.

Of course, you are free to ignore consumers and use the other parts of
Channels - like routing, session handling and authentication - with any
ASGI app, but they're generally the best way to write your application code.


Basic Layout
------------

A consumer is a subclass of either ``channels.consumer.AsyncConsumer`` or
``channels.consumer.SyncConsumer``. As these names suggest, one will expect
you to write async-capable code, while the other will run your code
synchronously in a threadpool for you.

Let's look at a basic example of a ``SyncConsumer``::

    from channels.consumer import SyncConsumer

    class EchoConsumer(SyncConsumer):

        def websocket_connect(self, event):
            self.send({
                "type": "websocket.accept",
            })

        def websocket_receive(self, event):
            self.send({
                "type": "websocket.send",
                "text": text,
            })

This is a very simple WebSocket echo server - it will accept all incoming
WebSocket connections, and then reply to all incoming WebSocket text frames
with the same text.

Consumers are structured around a series of named methods corresponding to the
``type`` value of the messages they are going to receive, with any ``.``
replaced by ``_``. The two handlers above are handling ``websocket.connect``
and ``websocket.receive`` messages respectively.

How did we know what event types we were going to get and what would be
in them (like ``websocket.receive`` having a ``text``) key? That's because we
designed this against the ASGI WebSocket specification, which tells us how
WebSockets are presented - read more about it in :doc:`ASGI </asgi>` - and
protected this application with a router that checks for a scope type of
``websocket`` - see more about that in :doc:`/topics/routing`.

Apart from that, the only other basic API is ``self.send(event)``. This lets
you send events back to the client or protocol server as defined by the
protocol - if you read the WebSocket protocol, you'll see that the dict we
send above is how you send a text frame to the client.

The ``AsyncConsumer`` is laid out very similarly, but all the handler methods
must be coroutines, and ``self.send`` is a coroutine::

    from channels.consumer import AsyncConsumer

    class EchoConsumer(AsyncConsumer):

        async def websocket_connect(self, event):
            await self.send({
                "type": "websocket.accept",
            })

        async def websocket_receive(self, event):
            await self.send({
                "type": "websocket.send",
                "text": text,
            })

When should you use ``AsyncConsumer`` and when should you use ``SyncConsumer``?
The main thing to consider is what you're talking to. If you call a slow
synchronous function from inside an ``AsyncConsumer`` you're going to hold up
the entire event loop, so they're only useful if you're also calling async
code (for example, using ``aiohttp`` to fetch 20 pages in parallel).

If you're calling any part of Django's ORM or other synchronous code, you
should use a ``SyncConsumer``, as this will run the whole consumer in a thread
and stop your ORM queries blocking the entire server.

We recommend that you **write SyncConsumers by default**, and only use
AsyncConsumers in cases where you know you are doing something that would
be improved by async handling (long-running tasks that could be done in
parallel) *and* you are only using async-native libraries.

If you really want to call a synchronous function from an ``AsyncConsumer``,
take a look at ``asgiref.SyncToAsync``, which is the utility that Channels
uses to run ``SyncConsumers`` in threadpools, and can turn any synchronous
callable into an asynchronous coroutine.


Generic Consumers
-----------------

What you see above is the basic layout of a consumer that works for any
protocol. Much like Django's *generic views*, Channels ships with
*generic consumers* that wrap common functionality up so you don't need to
rewrite it, specifically for HTTP and WebSocket handling.


WebsocketConsumer
~~~~~~~~~~~~~~~~~

Available as ``channels.generic.websockets.WebsocketConsumer``, this
wraps the verbose plain-ASGI message sending and receiving into handling that
just deals with text and binary frames::

    class MyConsumer(WebsocketConsumer):

        def connect(self):
            # Called on connection. Either call
            self.accept()
            # Or to reject the connection, call
            self.close()

        def receive(self, text_data=None, bytes_data=None):
            # Called with either text_data or bytes_data for each frame
            # You can call:
            self.send(text_data="Hello world!")
            # Or, to send a binary frame:
            self.send(bytes_data="Hello world!")
            # Want to force-close the connection? Call:
            self.close()
            # Or add a custom WebSocket error code!
            self.close(code=4123)

        def disconnect(self):
            # Called when the socket closes

You can also raise ``channels.exceptions.AcceptConnection`` or
``channels.exceptions.DenyConnection`` from anywhere inside the ``connect``
method in order to accept or reject a connection, if you want reuseable
authentication or rate-limiting code that doesn't need to use mixins.


JsonWebsocketConsumer
~~~~~~~~~~~~~~~~~~~~~

Available as ``channels.generic.websockets.JsonWebsocketConsumer``, this
works like ``WebsocketConsumer``, except it will auto-encode and decode
to JSON sent as WebSocket text frames.

The only API differences are:

* Your ``receive_json`` method must take a single argument, ``content``, that
  is the decoded JSON object.

* ``self.send_json`` takes only a single argument, ``content``, which will be
  encoded to JSON for you.

If you want to customise the JSON encoding and decoding, you can override
the ``encode_json`` and ``decode_json`` classmethods.
