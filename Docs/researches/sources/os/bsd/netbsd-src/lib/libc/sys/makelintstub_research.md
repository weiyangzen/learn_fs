# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/makelintstub

## Purpose
Generates C lint stubs for syscall assembly wrappers.

## Key Elements
Parses options `-n`, `-p`, `-o`, and `-s`; writes a generated-file header with many syscall-related includes; preprocesses `syscall.h` with `CPP -D_LIBC -C`; extracts syscall prototype comments; and emits ANSI plus K&R function definitions returning zero-equivalent values.

## Dependencies
Requires `CPP` in the environment, POSIX shell utilities, `sed`, `getopts`, and syscall-header comments of the form used by NetBSD.

## Behavior/Risks
Generation depends on syscall comment formatting and `eval set -f -- "$arglist"`, so malformed metadata can break output. `-n` and `-p` are mutually exclusive; `-p` strips a leading underscore from the syscall name.
