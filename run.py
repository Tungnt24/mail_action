from client import imap_client
from utils.logger import logger


def read_file(file_name: str) -> list:
    accounts = []
    with open(file_name, "r") as f:
        email, password = f.readline().split(",")
        accounts.append((email, password.strip()))
    return accounts


def imap_login(
    host: str, port: int, email: str, password: str
) -> imap_client.IMAPClient:
    client = imap_client.new_imap_client(host, port)
    imap_client.login(client, email, password)
    return client


def user_simulator(
    client: imap_client.IMAPClient, old_folder: str, new_folder: str
):
    message_ids = imap_client.get_mails(client, old_folder)
    for uid, message_id in message_ids:
        logger.info(f"MOVE mail uid={uid} from={old_folder} to={new_folder}")
        imap_client.move_message(client, [uid], old_folder, new_folder)

        new_uid = imap_client.get_uid_by_message_id(
            client, message_id, new_folder
        )
        if new_uid < 0:
            return
        logger.info(f"SEEN mail uid={new_uid}, folder={new_folder}")
        imap_client.set_flags(client, new_folder, [new_uid], imap_client.SEEN)

        logger.info(f"STAR mail uid={new_uid}, folder={new_folder}")
        imap_client.set_flags(
            client, new_folder, [new_uid], imap_client.FLAGGED
        )

        logger.info(f"UNSEEN mail uid={new_uid}, folder={new_folder}")
        imap_client.remove_flags(
            client, new_folder, [new_uid], imap_client.SEEN
        )


def main():
    accounts = read_file("")
    for account in accounts:
        email, password = account
        logger.info(f"simulator {email=}")
        client = imap_login("imap.gmail.com", 993, email, password)
        try:
            client.select_folder("Junk")
            user_simulator(client, "Junk", "INBOX")
        except Exception:
            user_simulator(client, "[Gmail]/Thư rác", "INBOX")


if __name__ == "__main__":
    main()