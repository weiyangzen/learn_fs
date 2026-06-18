# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.c

This is the outbound SMTP client. It parses delivery, TLS, auth, filtering, gateway, host, ping, and busted-MX flags; resolves the destination via `mxdial`; performs greeting/EHLO/HELO; optionally negotiates STARTTLS or direct TLS; optionally authenticates with CRAM-MD5, LOGIN, or PLAIN; sends MAIL FROM, RCPT TO, DATA, and QUIT; and maps replies to retry or permanent failure.

`data()` reads and parses message headers, converts bang addresses to `@`/route form, adds `Message-ID`, `From`, `To`, and `Date` when absent, prints headers with CRLF, dot-escapes body lines, and logs successful bytes sent. Filter mode writes converted message text to stdout without network SMTP commands.

Security-relevant paths include certificate thumbprint checking unless `-C`, no cleartext password auth unless encrypted or `-i`, zeroing password buffers, loopback MX rejection, and robust timeout/closed-pipe handling via `atnotify`.
