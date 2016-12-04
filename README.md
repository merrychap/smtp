# SMTP Implementation

### General description
This is smtp protocol implementation

### Requirements
- Python 3.*

### Arguments for running
Argument | Description
-------- | -----------
--fromaddr | "From" address for an email
--passwd | Password from "From" account for sending
--toaddrs | List of "To" addresses for an email
--subj | Subject of an email
--server | SMTP server for sending an email
--msg | Text of message
--dis-enc | Disable encryption
--attach | Attachments for an email
--archive | Archives all attachments to an archive

### Distribution mode
There are 3 modes of email distribution
- 1: For different recipients there are different instances of message
- 2: One message instance for all recipients
- 3: Custom mode. There you can specify different groups of distribution. For example, (1 2) (3 4). It means that there are 2 instances of message. By one for each group.

### How to send email?
```sh
$ python3 smtp_console.py [--keys ...]
```
If you didn't specify keys for running then you will be asked to input them

### Already done
- [X] Sending text emails
- [X] Email with attachments
- [X] Enable/disbale encryption
- [X] Automatic archiving attachments
- [X] Different distribution modes
