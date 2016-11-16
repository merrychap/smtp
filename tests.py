import unittest
from smtp import SMTP, SMTP_SERVERS


# class TestSMTP(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_sendmail(self):
#         smtp = SMTP(SMTP_SERVERS['google'])
#         smtp.auth('smtptest31337@gmail.com', 'poiuytrew')
#         self.assertEqual(smtp.sendmail('smtptest31337@gmail.com', ['smtptest31337@gmail.com'],
#                       'ti xuy'), True)
#
#
# if __name__ == '__main__':
#     unittest.main()


def main():
    smtp = SMTP(SMTP_SERVERS['google'])
    smtp.auth('smtptest31337@gmail.com', 'poiuytrew')
    recverr = smtp.sendmail('smtptest31337@gmail.com', ['smtptest31337@gmail.com',
                                                        'xyu'], 'ti xuy')
    print(recverr)
    for recv, err in recverr.items():
        print(recv)
        print(err, end='\n')


if __name__ == '__main__':
    main()
