# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/lis

This is a short rc wrapper for `aux/listen`.

Key behavior:
- Runs `aux/listen -t /sys/src/cmd/aux tcp`.

Filesystem relevance:
- Indirect service-start helper using trusted service directory configuration.
