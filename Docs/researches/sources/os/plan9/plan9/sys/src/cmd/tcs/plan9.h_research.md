# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/plan9.h

## Purpose

`plan9.h` supplies a small Plan 9 compatibility layer for non-Plan 9 builds of `tcs`.

## Contents

- Defines `Rune` as `unsigned long`.
- Defines `uchar` as `unsigned char`.
- Defines UTF constants:
  - `Runeerror 0x80`
  - `Runeself 0x80`
  - `UTFmax 6`
- Defines Plan 9-style argument parsing macros:
  - `ARGBEGIN`
  - `ARGEND`
  - `ARGF()`
  - `ARGC()`
- Declares `extern char *argv0`.

## Integration

Several converter files include `plan9.h` under non-Plan 9 builds, including `tcs.c`, `utf.c`, and conversion modules such as `conv_jis.c`, `conv_ksc.c`, `conv_big5.c`, `conv_gb.c`, and `conv_gbk.c`.

`tcs.c` uses `ARGBEGIN`/`ARGEND` for command-line parsing and owns the `argv0` definition.

## Notes

This file is portability glue. Its macro behavior is part of the command-line parser contract, so changes can affect all option parsing in `tcs`.
