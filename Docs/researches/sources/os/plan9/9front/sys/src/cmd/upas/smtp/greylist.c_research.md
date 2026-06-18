# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/greylist.c

This file implements SMTP greylisting for `smtpd`. It checks `/mail/grey/whitelist` for IP or subnet matches, tracks first-seen `(local IP, remote IP, recipient)` tuples under `/mail/grey/tmp`, and requires retry after `Nonspammin` and before `Nonspammax`.

If any recipient has a recent greylist entry, the remote IP is appended to the whitelist, optionally with reverse-domain metadata. Otherwise the server replies `451` and exits the transaction.

The implementation uses file creation/modification time as state and recursively creates parent directories. It rejects unsafe recipient path components before constructing greylist filenames.
