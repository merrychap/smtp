import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from mimetypes import guess_type
from email.encoders import encode_base64


def get_alias(filename):
    try:
        f = tuple(filename.rsplit(':', 1))
        return (f[0], f[1] if len(f) > 1 else os.path.basename(f[0]))
    except Exception:
        return (filename.filename, filename.filename)


class Email:
    def __init__(self, fromaddr, toaddr, subject, message, message_type='plain',
                 attachments=None, cc=None,message_encoding='utf-8'):
        self.email = MIMEMultipart()
        self.email['From'] = fromaddr
        self.email['To'] = toaddr
        self.email['Subject'] = subject
        if cc is not None:
            self.email['cc'] = cc
        text = MIMEText(message, message_type, message_encoding)
        self.email.attach(text)
        if attachments is not None:
            for filename in attachments:
                filename, alias = get_alias(filename)
                mimetype, encoding = guess_type(filename)
                mimetype = mimetype.split('/', 1)
                with open(filename, 'rb') as _file:
                    attachment = MIMEBase(mimetype[0], mimetype[1])
                    attachment.set_payload(_file.read())
                    encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment',
                                          filename=alias)
                    self.email.attach(attachment)

    def set_toaddr(self, toaddr):
        self.email['To'] = toaddr

    def __repr__(self):
        return self.email.as_string()
