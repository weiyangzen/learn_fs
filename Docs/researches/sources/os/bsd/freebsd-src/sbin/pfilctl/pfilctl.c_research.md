# File Research: sources/os/bsd/freebsd-src/sbin/pfilctl/pfilctl.c

## Purpose
Command-line control utility for FreeBSD pfil heads and hooks.

## Main Elements
- Dispatches abbreviated commands: `heads`, `hooks`, `link`, and `unlink`.
- Opens `/dev/pfil`.
- `listheads()` queries `PFILIOC_LISTHEADS`, resizes buffers if counts grow, and prints intercept points with in/out hooks.
- `listhooks()` queries `PFILIOC_LISTHOOKS` and prints hook module/ruleset/type.
- `hook()` parses `-i`, `-o`, `-a`, module:ruleset, and head name, then issues `PFILIOC_LINK`.

## Dependencies And Integration
Uses `<net/pfil.h>` ioctl ABI and PFIL device path.

## Risk Notes
Link/unlink mutates packet-filter hook attachment. Command matching permits abbreviations but rejects ambiguous matches.
