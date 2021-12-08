from client import imap_client

def read_file(file_name: str) -> list:
    accounts = []
    with open(file_name, "r") as f:
        email, password = f.readline().split(',')
        accounts.append((email, password.strip()))
    return accounts


def imap_login(host: str, port:int, email: str, password: str) -> imap_client.IMAPClient:
    client = imap_client.new_imap_client(host, port)
    imap_client.login(client, email, password)
    return client

def get_mail_junk(client: imap_client.IMAPClient, folder_name: str):
    client.select_folder(folder_name)
    uids = client.search()


