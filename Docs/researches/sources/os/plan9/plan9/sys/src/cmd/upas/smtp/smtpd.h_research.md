# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.h

Read fully: 69 lines, 1134 bytes. SHA-256 prefix: `643da5e72212a1eb`.

This is the SMTP daemon shared header. It defines filter/action states (`ACCEPT`, `REFUSED`, `DENIED`, `DIALUP`, `BLOCKED`, `DELAY`, `TRUSTED`, `NONE`), `MAXREJECTS`, linked-list types for senders/recipients, daemon globals, and daemon/spam/greylist/parser function prototypes.

Integration: included by `smtpd.c`, `smtpd.y`, `spam.c`, and `greylist.c`. It exposes session-global state such as `nci`, `dom`, `me`, `trusted`, `senders`, `rcvers`, and `rsysip`.

Risk notes: this header couples parser actions and policy modules to daemon globals. Any new filter state must be reflected in all switch statements in `smtpd.c` and `spam.c`.
