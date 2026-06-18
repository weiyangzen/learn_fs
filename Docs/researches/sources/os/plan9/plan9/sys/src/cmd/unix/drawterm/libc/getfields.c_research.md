# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getfields.c

This file splits strings into fields.

Key behavior:
- `getfields` tokenizes a string in place using a delimiter set.
- Supports merging adjacent delimiters or returning empty fields depending on `mflag`.

Important details:
- Replaces separators with NUL bytes and fills the caller's `args` array.
