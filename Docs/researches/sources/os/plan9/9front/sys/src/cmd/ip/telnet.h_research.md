# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnet.h

This header contains shared telnet constants, option state, negotiation handlers, and small I/O helpers used by both `telnet.c` and `telnetd.c`.

Key behavior:
- Defines Telnet IAC commands and common option codes.
- Maintains an `Opt opt[]` table with local/remote state and optional callbacks.
- Implements `control()`, `will()`, `wont()`, `doit()`, `dont()`, and subnegotiation parsing.
- Provides `send2()`, `send3()`, process note sending, fatal errors, and interrupt-tolerant read/write wrappers.

Research notes:
- This is a header with function definitions and global state, so each including program gets its own telnet engine instance.
- `noway` options are refused automatically.
