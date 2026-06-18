# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/auth.c

Authentication and user setup for `imap4d`. It supports CRAM-MD5 challenge/response, optional password verification by synthesizing the CRAM response, and setup through `auth_chuid`, user namespace construction, mailbox directory selection, and `upas/fs` initialization.

It also contains a ratifier-filesystem forwarding hack that periodically records the remote peer under `/mail/ratify/trusted` so authenticated IMAP sessions can enable outgoing SMTP forwarding.
