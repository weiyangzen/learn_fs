# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/util.c

## Purpose
Provides small utility callbacks and prompting helpers shared by `camcontrol`.

## Main Elements
- Global `verbose`.
- `iget()`: fetches and parses the next integer argument from `struct get_hook`.
- `cget()`: fetches the next string argument from `struct get_hook`.
- `arg_put()`: prints decoded integer, byte/string, or space-trimmed string values for format-driven SCSI argument output.
- `get_confirmation()`: repeatedly prompts for explicit `yes`/`no`.

## Dependencies And Integration
Uses `camcontrol.h` for parser hook structures and `usage()`. These helpers support older SCSI command argument formatting and dangerous-operation confirmation.

## Risk Notes
`iget()` uses `strtol()` without full validation of trailing characters. `arg_put()` allocates temporary buffers for string output and exits on allocation failure.
