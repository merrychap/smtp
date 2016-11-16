import socket
import copy
import ssl
import sys
import base64
import six
import logging


BUFFER_SIZE = 1024
logger = logging.getLogger(__name__)
SMTP_SERVERS = {
    'google': ('smtp.gmail.com', 465)
}


class SMTPException(Exception):
    pass


class SMTPServerIsNotAvailable(SMTPException):
    pass


class SMTPMailTransactionError(SMTPException):
    pass


class SMTPAuthenticationError(SMTPException):
    pass


def send_function(sender):
    def wrapper(self, data):
        sender(self, data + b'\r\n')
    return wrapper


def auth_function(auth):
    def wrapper(self, username, password):
        code, reply = auth(self, username, password)
        # if code != 334:
        #     raise SMTPAuthenticationError(code, reply)
        return (code, reply)
    return wrapper


class SMTP:
    def __init__(self, smtp_server):
        self.smtp_server = smtp_server
        self.encoding = 'ascii'
        self.auths = []

        self.init_socket()
        self.ehlo()

    def ehlo(self):
        code, reply = self.execute('EHLO a')
        if code != 250:
            raise SMTPServerIsNotAvailable('At the moment server '
                                           ' is not available')
        resp = reply.strip().split('\n')
        for line in resp:
            if 'AUTH' in line:
                self.handle_auth_line(line)
            elif 'SMTPUTF8' in line:
                self.encoding = 'utf-8'

    def handle_auth_line(self, line):
        for setting in line.split()[1:]:
            self.auths.append(setting)

    def init_socket(self):
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = ssl.wrap_socket(raw_socket,
                                      ssl_version=ssl.PROTOCOL_SSLv23)
        self.socket.connect((self.smtp_server))
        resp = self.socket.recv(BUFFER_SIZE)

    @send_function
    def send_data(self, data):
        self.socket.send(data)

    def recv_data(self):
        data = self.socket.recv(BUFFER_SIZE).decode(self.encoding)
        code = int(data[:3])
        reply = data[3:]
        return (code, reply)

    def is_bytes(self, data):
        try:
            data.decode(self.encoding)
            return True
        except AttributeError:
            return False

    def execute(self, command, message=False):
        if not self.is_bytes(command):
            command = command.encode(self.encoding)
        self.send_data(command)
        if not message:
            resp = self.recv_data()
            logger.info('[*] Repsonse: {0} {1}'.format(resp[0], resp[1][:-1]))
            return resp

    def execute_commands(self, *commands):
        for command in list(commands):
            if callable(command):
                command()
            else:
                self.execute(command) if isinstance(command, six.string_types) \
                else self.execute(*command)

    def base64encode(self, data):
        return base64.b64encode(data.encode(self.encoding))

    @auth_function
    def auth_plain(self, username, password):
        code, reply = self.execute('AUTH PLAIN')
        if code != 334:
            return (code, reply)
        return self.execute(self.base64encode('\0%s\0%s' % (username,
                                                            password)))

    @auth_function
    def auth_login(self, username, password):
        code, reply = self.execute('AUTH LOGIN')
        if code != 334:
            return (code, reply)

        code, reply = self.execute(self.base64encode(username))
        if code != 334:
            return (code, reply)

        return self.execute(self.base64encode(password))

    def auth(self, username, password):
        logger.info('\n' + '=' * 30 + '\n[*] Trying to login\n')

        AUTH_PLAIN = 'PLAIN'
        AUTH_LOGIN = 'LOGIN'
        pr_auths = [AUTH_PLAIN, AUTH_LOGIN]

        if len(self.auths) == 0:
            raise SMTPException('Server doesn\'t support SMPT AUTH')

        authmode = None
        for method in pr_auths:
            if method in self.auths:
                authmode = method
                break
        if authmode == AUTH_LOGIN:
            code, reply = self.auth_login(username, password)
        elif authmode == AUTH_PLAIN:
            code, reply = self.auth_plain(username, password)
        elif authmode is None:
            raise SMTPException('No suitable SMTP AUTH method for this server')

        if code not in [235, 503]:
            raise SMTPAuthenticationError(code, reply)
        logger.info('\n[+] Login successful\n' + '=' * 30 + '\n')
        return (code, reply)

    def mail(self, sender):
        code, reply = self.execute('MAIL FROM:<{}>'.format(sender))
        if code != 250:
            raise SMTPMailTransactionError(code, reply)
        return (code, reply)

    def rcpt(self, recv):
        return self.execute('RCPT TO:<{}>'.format(recv))

    def sendmail(self, sender, receivers, mail):
        self.mail(sender)
        recverr = {}

        for receiver in receivers:
            code, reply = self.rcpt(receiver)
            if code not in [250, 251]:
                recverr[receiver] = (code, reply)        
        self.execute_commands('DATA', (mail, True), '.', quit)
        return recverr

    def quit(self):
        self.execute('QUIT')
        self.socket.close()
