# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/log.c

Logging implementation for httpd. `logit` writes syslog entries, prefixing the remote system when available from `HSPriv`.

`writelog` writes a verbose alternating daily trace log containing request metadata and headers, and a Common Log Format-style file for `Reply:` messages. It extracts status and response size from the reply formats used by static and helper responses.
