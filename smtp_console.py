import logging
import argparse
import sys
import os
import zipfile
import traceback

from getpass import getpass

from smtp import SMTP, SMTP_SERVERS
from args_helper import Args_Helper
from email_c import Email, get_alias


ATTACH_ARCHIVE = 'attachs.zip'


def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)


def run_smtp(mode_data, smtp_server, dis_enc, fromaddr, password, toaddrs,
             data):
    print('[*] Connecting to server...')
    smtp = SMTP(SMTP_SERVERS[smtp_server], dis_enc)
    smtp.auth(fromaddr, password)
    send_by_mode(mode_data, smtp, fromaddr, toaddrs, data)
    print('[*] Message were sended')
    smtp.close()
    print('[*] Done')


def send_by_mode(mode_data, smtp, fromaddr, toaddrs, data):
    if mode_data[0] == 1:
        for addr in toaddrs:
            send_email(smtp, fromaddr, [addr], **data)
    elif mode_data[0] == 2:
        send_email(smtp, fromaddr, toaddrs, **data)
    elif mode_data[0] == 3:
        distr_list = mode_data[1]
        for distr in distr_list:
            send_email(smtp, fromaddr, distr, **data)


def send_email(smtp, fromaddr, toaddrs, subject, msg, attachs):
    str_toaddrs = addrs2str(toaddrs)
    print('[*] Preparing the email for %s' % str_toaddrs.replace(',', ' '))
    email = Email(fromaddr=fromaddr, toaddr=str_toaddrs,
                  subject=subject, message=msg, attachments=attachs)
    print('[*] Sending...')
    smtp.sendmail(fromaddr, toaddrs, str(email))


def addrs2str(addrs):
    addrs_str = ''
    for addr in addrs:
        addrs_str += addr + ','
    return addrs_str[:-1]

def attach2archive(attachs):
    zf = zipfile.ZipFile(ATTACH_ARCHIVE, mode='w')
    try:
        print('[*] Attachments is converted to zip archive')
        for attach in attachs:
            zf.write(get_alias(attach)[0])
    finally:
        zf.close()
    return zf


def remove_archive():
    os.remove(ATTACH_ARCHIVE)


def main():
    setup_logging()

    parser = Args_Helper()
    mode_data, data = parser.get_params()

    try:
        if data['archive']:
            data['data']['attachs'] = [attach2archive(data['data']['attachs'])]
            del data['archive']
        run_smtp(mode_data=mode_data, **data)
    except Exception as e:
        traceback.print_exc(e)
        print('[-] Exception was occured')
    finally:
        remove_archive()

if __name__ == '__main__':
    main()
