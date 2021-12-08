from typing import List
from imapclient import IMAPClient

from utils.logger import logger


FLAGS = "FLAGS"
FLAGGED = b"\\Flagged"
SEEN = b"\\Seen"
RECENT = b"\\Recent"
DELETED = b"\\Deleted"
DRAFT = b"\\Draft"
MOVED = "$Moved"


def new_imap_client(
    host: str, port: int = 143, ssl: bool=True
) -> IMAPClient:
    """Connect to imap server.

    Return imapclient instance or None if any exception occurs

    """
    try:
        client = IMAPClient(host, port, ssl)
        if not ssl:
            client.starttls()
        return client
    except Exception as e:
        logger.error(
            "Failed to connect to imap server: %s:%s, reason: %r",
            host,
            port,
            e,
        )


def login(client: IMAPClient, username: str, password: str) -> bool:
    """Login client using username and password

    client is IMAPClient instance

    """
    try:
        client.login(username, password)
        return True
    except Exception as e:
        logger.error("Could not login: %r", e)
        return False


def move_message(
    client: IMAPClient, uids: List[int], old_folder: str, new_folder: str
):
    """
    message_ids: list of message imap id
    flag: IMAP flags, \Seen \Answered \Flagged \Deleted \Draft \Recent
    """
    try:
        client.select_folder(old_folder)
        return client.move(uids, new_folder)
    except Exception as e:
        logger.error("Could not set flag for message: %r", e)
        return False


def set_flags(
    client: IMAPClient, folder: str, uids: List[int], flags: List[str]
) -> bool:
    """
    message_ids: list of message imap id
    flags: list of IMAP flags, \Seen \Answered \Flagged \Deleted \Draft \Recent
           or custom keywords
    """
    try:
        client.select_folder(folder)
        client.set_flags(uids, flags)
        return True
    except Exception as e:
        logger.error("Could not set flag for message: %r", e)
        return False


def remove_flags(
    client: IMAPClient, folder: str, uids: List[int], flags: List[str]
) -> bool:
    """
    message_ids: list of message imap id
    flags: list of IMAP flags, \Seen \Answered \Flagged \Deleted \Draft \Recent
           or custom keywords
    """
    try:
        client.select_folder(folder)
        client.remove_flags(uids, flags)
        return True
    except Exception as e:
        logger.error("Could not set flag for message: %r", e)
        return False
