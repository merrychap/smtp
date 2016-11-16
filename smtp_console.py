import logging

from getpass import getpass
from smtp import SMTP, SMTP_SERVERS


def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)


def run_smtp():
    smtp_server = input('Choose smtp server, %s: ' % [s for s in \
                                                      SMTP_SERVERS.keys()])

    fromaddr = input('From: ')
    username = fromaddr
    password = getpass('Your password: ')

    toaddrs = input('To: ')
    msg = ''

    print('Enter message: (end with ^D)')
    while 1:
        try:
            line = input()
            msg += line
        except EOFError:
            break

    smtp = SMTP(SMTP_SERVERS[smtp_server])
    smtp.auth(fromaddr, password)
    recverr = smtp.sendmail(fromaddr, toaddrs.split(' '), msg)
    for recv, err in recverr.items():
        print(recv)
        print(err, end='\n')
    print('[+] Message were sended')


def main():
    setup_logging()
    run_smtp()


if __name__ == '__main__':
    main()
