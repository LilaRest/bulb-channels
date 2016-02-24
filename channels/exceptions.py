class ConsumeLater(Exception):
    """
    Exception that says that the current message should be re-queued back
    onto its channel as it's not ready to be consumd yet (e.g. global order
    is being enforced)
    """
    pass


class ResponseLater(Exception):
    """
    Exception raised inside a Django view when the view has passed
    responsibility for the response to another consumer, and so is not
    returning a response.
    """
    pass
