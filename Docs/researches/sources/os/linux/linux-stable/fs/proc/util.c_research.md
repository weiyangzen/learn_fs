# File Research: sources/os/linux/linux-stable/fs/proc/util.c

Small proc utility file.

Key points:
- Implements `name_to_int()` for converting dentry qstr names to unsigned integers.
- Rejects leading-zero multi-character names, non-digits, and overflow.
- Returns `~0U` as invalid sentinel.

Dependencies/contracts:
- Used by proc PID/name lookup code to parse numeric directory names.
