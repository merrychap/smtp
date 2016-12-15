import unittest
from unittest.mock import patch

from smtp import SMTP, SMTP_SERVERS, SMTPServerIsNotAvailable, SMTPException
from smtp import SMTPAuthenticationError, SMTPMailTransactionError


def create_smtp(server='google', dis_enc=True):
    return SMTP(SMTP_SERVERS[server], dis_enc)


class TestSMTP(unittest.TestCase):
    def setUp(self):
        self.sender = 'mail@domain.ext'

    @patch.object(SMTP, 'execute')
    def test_ehlo_success(self, mock_execute):
        mock_execute.return_value = (250, (
            'smtp.gmail.com at your service, [212.193.78.207]\n'
            '250 SIZE 35882577\n'
            '250 8BITMIME\n'
            '250 AUTH LOGIN XOAUTH2 PLAIN CLIENTTOKEN OAUTHBEARER XOAUTH\n'
            '250 ENHANCEDSTATUSCODES\n'
            '250 PIPELINING\n'
            '250 CHUNKING\n'
            '250 SMTPUTF8\n')
        )
        smtp = create_smtp()
        smtp.ehlo()
        self.assertEqual(smtp.encoding, 'utf-8')
        self.assertEqual(smtp.auths, ['LOGIN', 'XOAUTH2', 'PLAIN',
                                      'CLIENTTOKEN', 'OAUTHBEARER',
                                      'XOAUTH'])

    @patch.object(SMTP, 'execute')
    def test_ehlo_fail(self, mock_execute):
        mock_execute.return_value = (501, 'EHLO Invalid domain address.')
        smtp = create_smtp()
        with self.assertRaises(SMTPServerIsNotAvailable):
            smtp.ehlo()

    @patch.object(SMTP, 'execute')
    def test_auth_attrs_fails(self, mock_execute):
        ehlo_without_auth = (250, (
            'smtp.gmail.com at your service, [212.193.78.207]\n'
            '250 SIZE 35882577\n'
            '250 8BITMIME\n'
            '250 ENHANCEDSTATUSCODES\n'
            '250 PIPELINING\n'
            '250 CHUNKING\n'
            '250 SMTPUTF8\n')
        )
        split_ehlo = ehlo_without_auth[1].split('\n')
        ehlo_without_auth_method = (250, '\n'.join(split_ehlo[2:] +
                                                   ['250 AUTH'] +
                                                   split_ehlo[:2]))
        for ehlo_resp in [ehlo_without_auth, ehlo_without_auth]:
            mock_execute.return_value = ehlo_resp
            smtp = create_smtp()
            smtp.ehlo()
            with self.assertRaises(SMTPException):
                smtp.auth('test', 'test')

    def run_auths(self, mock_plain, mock_login, message, error=False):
        auths = ['PLAIN', 'LOGIN']
        auth_functions = [mock_plain, mock_login]
        for auth_mode, auth_func in zip(auths, auth_functions):
            auth_func.return_value = message
            smtp = create_smtp()
            smtp.auths = [auth_mode]
            if error:
                with self.assertRaises(SMTPAuthenticationError):
                    smtp.auth('test', 'test')
            else:
                self.assertEqual(smtp.auth('test', 'test'), message)

    @patch.object(SMTP, 'auth_login')
    @patch.object(SMTP, 'auth_plain')
    def test_auth_failed_plain_and_login(self, mock_plain, mock_login):
        self.run_auths(mock_plain, mock_login, (535, 'Authentication failed.'
                       ' Restarting authentication process.'), True)

    @patch.object(SMTP, 'auth_login')
    @patch.object(SMTP, 'auth_plain')
    def test_auth_success_plain_and_login(self, mock_plain,
                                          mock_login):
        self.run_auths(mock_plain, mock_login, (235, '2.7.0 Authentication '
                       'successful'))

    @patch.object(SMTP, 'execute')
    def test_mail_transaction_fail(self, mock_execute):
        fail_message = (550, ('Invalid syntax. Syntax should be MAIL '
                              'FROM:<userdomain>[crlf]'))
        mock_execute.return_value = fail_message
        smtp = create_smtp()
        with self.assertRaises(SMTPMailTransactionError):
            smtp.mail(self.sender)

    @patch.object(SMTP, 'execute')
    def test_mail_success(self, mock_execute):
        success_msg = (250, '2.1.0 mail@domain.ext... Sender ok')
        mock_execute.return_value = success_msg
        smtp = create_smtp()
        self.assertEqual(smtp.mail(self.sender), success_msg)

    

def main():
    unittest.main()


if __name__ == '__main__':
    main()
