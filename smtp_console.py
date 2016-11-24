import logging
import argparse
import sys

from getpass import getpass
from smtp import SMTP, SMTP_SERVERS

from args_helper import Args_Helper


def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)


def run_smtp(fromaddr, password, toaddrs, smtp_server, msg, dis_enc):
    smtp = SMTP(SMTP_SERVERS[smtp_server], dis_enc)
    smtp.auth(fromaddr, password)
    recverr = smtp.sendmail(fromaddr, toaddrs.split(' '), msg)
    print(recverr)
    for recv, err in recverr.items():
        print(recv)
        print(err, end='\n')
        print()
    print('[+] Message were sended')


def main():
    parser = Args_Helper()
    data = parser.get_params()

    setup_logging()
    run_smtp(**data)


if __name__ == '__main__':
    main()
