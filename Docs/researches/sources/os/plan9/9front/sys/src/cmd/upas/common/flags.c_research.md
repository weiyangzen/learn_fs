# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/flags.c

This file converts between compact textual mail flag strings and internal flag bits.

Key behavior:
- `flagtab` maps characters `a D d f r s S` to answered/deleted/draft/flagged/recent/seen/stored.
- `flagbuf` emits a fixed-width flag string, using `-` for unset flags.
- `buftoflags` parses a fixed-position buffer into bits.
- `txflags` applies a stream of flag operations with optional `+` or `-` prefixes and returns `"bad flag"` for unknown characters.

Integration and risks:
- Used by upas/fs info files, control writes, IMAP flag mapping, and helper utilities.
- `buftoflags` assumes the input has enough positions for all known flags.
