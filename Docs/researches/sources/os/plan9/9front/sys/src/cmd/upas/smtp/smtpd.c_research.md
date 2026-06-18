# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.c

`smtpd.c` is the inbound SMTP server implementation. It initializes connection metadata, policy configuration, TLS/auth flags, blocked/trusted IP state, parser state, and a long alarm, then delegates protocol parsing to `smtpd.y`.

It implements SMTP verbs, relay checks, sender/recipient validation, sender-domain verification, greylisting, blocked-message dumping, message piping to `upas/send`, header parsing and rewriting, forged-domain warnings, received-line insertion, dot unescaping, UTF header validation, rejection throttling, TLS server wrapping, and AUTH PLAIN/LOGIN/CRAM-MD5.

Policy integrates `/mail/lib/smtpd.conf`, `/mail/ratify`, `/mail/lib/senders`, `/mail/lib/names.blocked`, optional `validateaddress`, optional `validatesender`, optional `validateattachment` via other tools, per-user spam opt-out, and trusted-network handling. The file is the main inbound mail security boundary.
