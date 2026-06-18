# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.c

Read fully: 1751 lines, 36261 bytes. SHA-256 prefix: `b69f23f52000c306`.

This is the inbound SMTP daemon. It handles process setup, peer discovery, configuration, SMTP replies, greeting, command actions from `smtpd.y`, sender/recipient validation, filtering, DATA ingestion, local mailer execution, STARTTLS, and AUTH.

Startup reads options for authentication, TLS cert, no-relay, greylisting, sender-domain validation, banned IPs, mailer path, and logging/debugging. It gets `NetConnInfo`, parses the remote IP, loads spam config through `getconf()`, rejects banned peers, initializes the command parser, sends a deliberately slow greeting, and parses commands under an alarm.

Policy flow: `hello()` rejects clients pretending to be the local domain or bogus domains; `sender()` enforces authentication when requested and classifies sender/IP through spam policy; `receiver()` validates recipients, sender-IP authorization pairs, and relay rules; `data()` checks envelope state, optional sender MX validation, greylist/filter state, then accepts or rejects the message.

`pipemsg()` writes the accepted message to the configured mailer, adding a Unix `From ` envelope line, `Received`, missing `From`/`To`, and forged-header warnings; it parses the first 16 KiB of headers and handles SMTP dot unescaping. `startcmd()` chooses between real mailer execution, spam dump-to-file, temporary delay, or hard rejection.

TLS and auth: `starttls()` wraps stdin/stdout with `tlsServer()` after reading a certificate. `auth()` supports PLAIN, LOGIN, and CRAM-MD5, requires encryption for clear-password modes unless explicitly allowed, scrubs some password buffers, and marks authenticated clients as trusted.

Integration: generated command parser `smtpd.y` calls functions here; spam policy is in `spam.c`; greylisting in `greylist.c`; header parsing from `rfc822.y`; local delivery typically invokes `upas/send`.

Risk notes: many policy decisions are global/session state. The daemon intentionally kills child mailer processes on alarms. Header parsing assumes the full header is within 16 KiB. DATA success/failure semantics depend on both pipe status and child exit status.
