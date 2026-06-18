# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.c

Read fully: 1136 lines, 21007 bytes. SHA-256 prefix: `0091124574180032`.

This is the outbound SMTP client used by upas. It parses command-line options for TLS, authentication, gateway, host/domain, filter-only mode, ping timing, busted MX skips, and insecure behavior; then dials the destination, performs SMTP greeting, sends envelope commands, transmits DATA, and reports retry/permanent failures.

Connection setup uses `mxdial()`. `hello()` handles banner/EHLO/HELO, STARTTLS discovery, TLS upgrade via `dotls()`, certificate thumbprint validation through `/sys/lib/tls/smtp`, and AUTH LOGIN/PLAIN via Plan 9 auth helpers. `mailfrom()` and `rcptto()` generate envelope commands and classify 2xx/5xx/other replies.

`data()` reads and parses headers, invokes `rfc822.y`, adds missing `Message-ID`, `From`, `To`, and `Date` fields, converts bang addresses to `@`/route-address form, preserves header whitespace, dot-stuffs message data, and normalizes newlines to CRLF. Filter mode writes the transformed message to stdout without an SMTP session.

Address helpers include `bangtoat()`, `convertheader()`, `fixrouteaddr()`, `domainify()`, and timezone rewriting for generated dates. Reply handling supports multiline SMTP replies.

Integration: send rewrite rules invoke this program for remote delivery. It shares parser structures from `smtp.h`/`rfc822.y` and transport resolution from `mxdial.c`.

Risk notes: global state drives the SMTP transaction. TLS thumbprint failure after STARTTLS is treated as permanent unless unknown-secure mode is allowed; some error paths intentionally call `_exits()` to avoid flushing closed Bio streams.
