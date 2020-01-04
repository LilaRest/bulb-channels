from django.conf import settings
from bulb.contrib.auth.node_models import get_anonymoususer_node_model, get_user_node_model
from bulb.contrib.sessions.node_models import Session
from bulb.db.node_models import BaseNodeAndRelationship
from bulb.db import gdbh
from django.utils.functional import LazyObject

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
import base64


AnonymousUser = get_anonymoususer_node_model()
User = get_user_node_model()

@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    if "session" not in scope:
        raise ValueError(
            "Cannot find session in scope. You should wrap your consumer in SessionMiddleware."
        )
    session_key = scope["session"]._wrapped._SessionBase__session_key
    user_node = gdbh.w_transaction("MATCH (:Session {session_key: '%s'})-[:IS_SESSION_OF]->(n:User) RETURN n" % session_key)[0]["n"]
    user = BaseNodeAndRelationship.build_fake_instance(user_node, User)

    return user or AnonymousUser()


class UserLazyObject(LazyObject):
    """
    Throw a more useful error message when scope['user'] is accessed before it's resolved
    """

    def _setup(self):
        raise ValueError("Accessing scope user before it is ready.")


class AuthMiddleware(BaseMiddleware):
    """
    Middleware which populates scope["user"] from a Django session.
    Requires SessionMiddleware to function.
    """

    def populate_scope(self, scope):
        # Make sure we have a session
        if "session" not in scope:
            raise ValueError(
                "AuthMiddleware cannot find session in scope. SessionMiddleware must be above it."
            )
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)


# Handy shortcut for applying all three layers at once
AuthMiddlewareStack = lambda inner: CookieMiddleware(
    SessionMiddleware(AuthMiddleware(inner))
)
