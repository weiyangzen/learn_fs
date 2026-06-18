# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.h

`smtpd.h` declares SMTP server policy states, linked-list helpers, globals shared between the C server and yacc command parser, and handler prototypes for SMTP commands and policy checks.

The state enum distinguishes accepted, refused, denied, dialup-blocked, delayed, trusted, and none/error classifications. Exports include connection info, sender/receiver lists, trusted flag, remote IP bytes, greylist, auth, data, reset, and spam-policy APIs.
