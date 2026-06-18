# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mslib.c

Read status: complete.

Purpose: Microsoft Windows platform support variant for the Ghostscript graphics library rather than the interpreter.

Main logic:
- Under `CHECK_INTERRUPTS`, defines `gp_check_interrupts` to always return `0`.

Filesystem/storage relevance:
- None. It is a polling stub for library builds.
