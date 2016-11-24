from smtp import SMTP_SERVERS

import argparse


class Args_Helper:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--fromaddr', action='store', type=str,
                            help='From address')
        self.parser.add_argument('--toaddrs', action='store', type=str,
                            help='To addresses')
        self.parser.add_argument('--server', action='store', type=str,
                            help='SMTP server')
        self.parser.add_argument('--passwd', action='store', type=str,
                            help='Password for login')
        self.parser.add_argument('--msg', action='store', type=str,
                            help='Message for recipients')
        self.parser.add_argument('--dis-enc', action='store_true',
                            help='Disables encryption')

    def get_params(self):
        args = self.parser.parse_args()

        if not args.server:
            smtp_server = input('Choose smtp server, %s: ' % \
                                [s for s in SMTP_SERVERS.keys()])
        else:
            smtp_server = args.server

        fromaddr = input('From: ') if not args.fromaddr else args.fromaddr
        password = getpass('Your password: ') if not args.passwd else args.passwd

        username = fromaddr

        toaddrs = input('To: ') if not args.toaddrs else args.toaddrs

        msg = args.msg

        if not msg:
            print('Enter message: (end with ^D)')
            for line in sys.stdin:
                msg += line

        return {
            'fromaddr': fromaddr,
            'password': password,
            'toaddrs': toaddrs,
            'smtp_server': smtp_server,
            'msg': msg,
            'dis_enc': args.dis_enc
        }
