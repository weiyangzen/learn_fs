# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nsec.c

This file returns nanosecond time.

Key behavior:
- `nsec` reads `/dev/bintime`, decodes big-endian seconds/fraction fields, and returns nanoseconds.
- `be2vlong` decodes big-endian 64-bit values.

Important details:
- Caches the opened `/dev/bintime` fd.
- Converts binary time fraction to nanoseconds.
