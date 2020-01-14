import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="../zuliprc")


def send_private_zulip(email: str, msg: str) -> bool:
    response = client.send_message({
        "type": "private",
        "to": email,
        "content": msg
    })
    return response['result'] == 'success'
