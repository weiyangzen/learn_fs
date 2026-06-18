# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/main.c

## Purpose

Command-line entry point and interactive prompt handler for `fsck_msdosfs`.

## Main Behavior

- Parses options:
  - `-f`: do not skip clean filesystems
  - `-F`: unsupported background check probe, exits 5
  - `-n`: assume no
  - `-y`: assume yes
  - `-p`: preen mode
  - `-M`: disable mmap
  - `-B`, `-C`: accepted for compatibility/no-op
- Iterates over filesystems, sets device name, and calls `checkfilesys()`.
- Returns the maximum filesystem check result.

## `ask()`

Central yes/no prompt function:
- Honors `alwaysyes`, `alwaysno`, and `rdonly`.
- In preen mode, automatically applies default answers and prints `FIXED` when default is yes.
- Otherwise prompts on stdin.

## Integration Notes

Defines global option variables declared in `ext.h`.
