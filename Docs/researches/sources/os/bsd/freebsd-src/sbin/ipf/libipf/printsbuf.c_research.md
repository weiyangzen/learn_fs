# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printsbuf.c

IPFilter scan-buffer printer.

Key behavior:
- When `IPFILTER_SCAN` is enabled, prints `ISC_TLEN` bytes with printable characters direct and others as octal escapes.
- Otherwise provides a no-op stub.

Research notes:
- Keeps builds working when scan support is disabled.
