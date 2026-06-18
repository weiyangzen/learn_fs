# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/error.c

Provides fatal `error` and verbose `trace` helpers. `error` re-enables the sequencer, prefixes messages with `argv0`, optionally mirrors details to stdout when verbose, writes to stderr, and exits with `"error"`.

`trace` prints only when `vflag` or `Vflag` is active, resets register-dump line formatting when needed, and mirrors to the console with `print` when `Vflag` is set.

This file is central to failure handling across all hardware probing and register programming paths.
