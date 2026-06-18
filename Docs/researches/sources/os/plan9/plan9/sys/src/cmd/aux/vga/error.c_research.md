# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/error.c

Fatal error and trace support for the VGA utility.

Core behavior:
- `error()` turns the sequencer back on, formats `argv0: message`, optionally echoes message body to stdout when verbose, flushes stdout, writes to stderr, and exits with status `error`.
- `trace()` writes diagnostic text to stdout when `vflag` or `Vflag` is set and additionally to standard print output when `Vflag` is set.
- Maintains global verbosity flags `vflag` and `Vflag`.

Dependencies and integration:
- Used by almost every VGA helper.
- Calls `sequencer(0, 1)` before fatal exit to avoid leaving display sequencer disabled.

Notable risks:
- Fatal path assumes display recovery through `sequencer()` is always safe enough to attempt.
