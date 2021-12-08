from imapclient import IMAPClient

from utils.logger import logger
from typing import List
import time


FLAGS = "FLAGS"
FLAGGED = b"\\Flagged"
SEEN = b"\\Seen"
RECENT = b"\\Recent"
DELETED = b"\\Deleted"
DRAFT = b"\\Draft"
MOVED = "$Moved"
MESSAGE_ID = b'BODY[HEADER.FIELDS (MESSAGE-ID)]'
SEARCH_CRITERIA_BY_MESSAGE_HEADER_ID = 'HEADER "Message-ID" "{}"'


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
    uids: list of message imap id
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
    uids: list of message imap id
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
    uids: list of message imap id
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


def get_uid_by_message_id(client: IMAPClient, msg_header_id: str, folder_name: str) -> int:
    i = 0
    while i < 3:
        try:
            client.select_folder(folder_name)
            res = client.search(
                SEARCH_CRITERIA_BY_MESSAGE_HEADER_ID.format(msg_header_id)
            )
            return res[-1]
        except IMAPClient.AbortError as ae:
            logger.error('[{}] Could not get message AbortedError: ex={}'.format(
                msg_header_id, ae
            ))
            time.sleep(i * 2)
            i = i + 1
            continue
        except Exception as e:
            logger.error('[{}] Could not get message:  ex={}'.format(
                msg_header_id, e
            ))
        break
    return -1


def get_message_id(res: dict, uid: int) -> str:
    message_id = res.get(uid).get(MESSAGE_ID)
    if message_id:
        return message_id.decode('utf-8').split(":")[-1].strip()
    return ""


def get_mails(client: IMAPClient, folder_name: str, status: str="UNSEEN") -> list:
    try:
        client.select_folder(folder_name)
        uids = client.search(status)
        result = []
        if uids:
            for uid in uids:
                res = client.fetch([uid], [MESSAGE_ID])
                message_id = get_message_id(res, uid)
                if not message_id:
                    continue
                result.append((uid, message_id))
        return result
    except Exception as e:
        logger.info(f"Couldn't get mail: ex={e}")
        return []