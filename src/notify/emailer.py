import yagmail

def send_email(smtp_user: str, smtp_password: str, to_addrs, subject: str, body: str):
    yag = yagmail.SMTP(smtp_user, smtp_password)
    yag.send(to=to_addrs, subject=subject, contents=body)
