from smtp import SMTP_SERVERS
from getpass import getpass

import argparse
import sys
import re


class Args_Helper:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--fromaddr', action='store', type=str,
                                 help='From address')
        self.parser.add_argument('--passwd', action='store', type=str,
                                 help='Password for login')
        self.parser.add_argument('--toaddrs', nargs='*',
                                 help='To addresses')
        self.parser.add_argument('--server', action='store', type=str,
                                 help='SMTP server')
        self.parser.add_argument('--subj', action='store', type=str,
                                 help='Subject of the message')
        self.parser.add_argument('--msg', action='store', type=str,
                                 help='Message for recipients')
        self.parser.add_argument('--attach', nargs='*',
                                 help='Attachments for email')
        self.parser.add_argument('--archive', action='store_true',
                                 help='Archives all attachments')
        self.parser.add_argument('--dis-enc', action='store_true',
                                 help='Disables encryption')
        self.parser.add_argument('--distr-mode', action='store', type=int,
                                 help='Distribution mode')

    def get_params(self):
        args = self.parser.parse_args()
        if not args.server:
            smtp_server = input('Choose smtp server, %s: ' % \
                                list(SMTP_SERVERS.keys()))
        else:
            smtp_server = args.server
        fromaddr = input('From: ') if not args.fromaddr else args.fromaddr
        password = getpass('Your password: ') if not args.passwd else args.passwd
        toaddrs = input('To: ') if not args.toaddrs else args.toaddrs
        subject = input('Subject: ') if not args.subj else args.subj

        username = fromaddr
        msg = args.msg

        if not msg:
            msg = ''
            print('Enter message: (end with ^D)')
            for line in sys.stdin:
                msg += line
        if args.distr_mode:
            mode = args.distr_mode
            mode_data = (mode,)
            if mode == 3:
                mode_data = self.enter_groups_distr_mode(toaddrs)
        else:
            mode_data = self.enter_mode(toaddrs)
            mode = mode_data if not isinstance(mode_data, tuple) else mode_data[0]
        if mode not in [1, 2, 3]:
            print('[-] Error occured')
            sys.exit()
        return (mode_data, {
            'fromaddr': fromaddr,
            'password': password,
            'toaddrs': toaddrs,
            'smtp_server': smtp_server,
            'dis_enc': args.dis_enc,
            'data': { 'msg': msg, 'subject': subject, 'attachs': args.attach },
            'archive': args.archive
        })

    def enter_mode(self, toaddrs):
        print('Input distribution mode:')
        print('1: Message are sended to all recipients seperately')
        print('2: One message for all recipients')
        print('3: Custom mode. Enter groups of distribution')

        try:
            mode = int(input('Enter mode: '))
        except NameError:
            print ('[-] Error occured')
            sys.exit()

        if mode == 3:
            return self.enter_groups_distr_mode(toaddrs)
        return (mode,)

    def enter_groups_distr_mode(self, toaddrs):
        import re

        reg = re.compile(r'\([\d+\ +]+\)')
        distr_list = input('Enter distribution list: ')
        distr_list = reg.findall(distr_list)
        or_distr = []
        for distr in distr_list:
            distr = list(filter(None, distr[1:-1].split(' ')))
            email_distr = []
            for num in distr:
                email_distr.append(toaddrs[int(num) - 1])
            or_distr.append(email_distr)
        return (3, or_distr)
