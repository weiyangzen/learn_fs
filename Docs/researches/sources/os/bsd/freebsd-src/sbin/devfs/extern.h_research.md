# File Research: sources/os/bsd/freebsd-src/sbin/devfs/extern.h

## Purpose
Shared declarations for the `devfs` command implementation.

## Main Elements
- Includes kernel devfs ioctl structures from `<fs/devfs/devfs.h>`.
- Defines command table types.
- Declares `rule_main`, `ruleset_main`, parsing helpers, and global `mpfd`.

## Dependencies And Integration
Included by `devfs.c` and `rule.c`.
