# File Research: sources/os/plan9/plan9/sys/src/9/bcm/syscall.c

This file is a one-line wrapper including `../kw/syscall.c`.

It reuses the `kw` syscall implementation for the BCM ARM kernel.

Integration points: called from `lexception.s` `_vsvc` and declared through standard kernel syscall interfaces.

Risk notes: actual syscall dispatch, argument handling, and tracing live in the included `kw` source.
