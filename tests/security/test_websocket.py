import pytest

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.security.websocket import OriginValidator
from channels.testing import WebsocketCommunicator


@pytest.mark.asyncio
async def test_origin_validator():
    """
    Tests that OriginValidator correctly allows/denies connections.
    """
    # Make our test application
    application = OriginValidator(AsyncWebsocketConsumer, ["allowed-domain.com"])
    # Test a normal connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"http://allowed-domain.com")])
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()
    # Test a bad connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"http://bad-domain.com")])
    connected, _ = await communicator.connect()
    assert not connected
    await communicator.disconnect()
    # Make our test application, bad pattern
    application = OriginValidator(AsyncWebsocketConsumer, ["*.allowed-domain.com"])
    # Test a bad connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"http://allowed-domain.com")])
    connected, _ = await communicator.connect()
    assert not connected
    await communicator.disconnect()
    # Make our test application, good pattern
    application = OriginValidator(AsyncWebsocketConsumer, [".allowed-domain.com"])
    # Test a normal connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"http://www.allowed-domain.com")])
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()
    # Make our test application, with scheme://domain[:port] for http
    application = OriginValidator(AsyncWebsocketConsumer, ["http://allowed-domain.com"])
    # Test a normal connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"http://allowed-domain.com")])
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()
    # Test a bad connection
    communicator = WebsocketCommunicator(application, "/", headers=[(b"origin", b"https://bad-domain.com:443")])
    connected, _ = await communicator.connect()
    assert not connected
    await communicator.disconnect()
