# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushssl.c

This file pushes Plan 9's SSL device layer over an fd.

Key behavior:
- `pushssl` opens `#D/ssl`, attaches the fd, writes algorithm/secrets to control files, and returns a data fd/control fd.

Important details:
- Uses Plan 9 device-file conventions rather than OpenSSL APIs.
