# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/greylist.c

Read fully: 317 lines, 7725 bytes. SHA-256 prefix: `6a137964fda6f57a`.

This file implements SMTP greylisting for `smtpd`. Unknown callers are rejected temporarily until they retry after `Nonspammin` and before `Nonspammax`; successful retry promotes the sender IP into `/mail/grey/whitelist`.

`onwhitelist()` checks IP or CIDR entries in the whitelist. Bare IPv4 entries default to `/24`, intentionally accepting nearby mail hosts from large providers; IPv6 defaults to `/128`. `mkdirs()`/`mkpdirs()` create greylist directory paths, and `addgreylist()` creates or reads per-recipient greylist files under `/mail/grey/tmp/<local-ip>/<remote-ip>/<recipient>`.

`vfysenderhostok()` is the daemon-facing entry point. It returns immediately for whitelisted callers, checks every recipient for recent greylist state, appends the remote IP and optional DNS name to the whitelist on success, or replies `451` and exits on first-time/too-soon/too-late attempts.

Integration: called from `smtpd.c` when greylisting is enabled after sender/recipient policy checks. Uses `nci`, `rsysip`, `rcvers`, and `reply()` from the daemon.

Risk notes: filesystem state is the greylist database. Permissions, path length, or file-server semantics can affect behavior. Recipient names containing `/`, empty names, `.`, and `..` are rejected to avoid path traversal.
