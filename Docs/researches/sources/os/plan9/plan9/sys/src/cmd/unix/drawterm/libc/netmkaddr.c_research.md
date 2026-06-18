# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/netmkaddr.c

This file constructs Plan 9 network address strings.

Key behavior:
- `netmkaddr` combines a linear address with default network and service components when missing.

Important details:
- Understands Plan 9 address separators such as `!`.
- Used by dial/auth networking code.
