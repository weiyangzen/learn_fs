# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/log.c

HTTP logging implementation. `logit` writes syslog messages, prefixing the remote system when available from `HSPriv`.

`writelog` writes two styles of access log: a verbose alternating daily trace log with request headers and request metadata, and a Common Log Format-style log in `logall[2]` for `Reply:` messages. It extracts status and response size from selected reply format strings used by `sendfd.c`.
