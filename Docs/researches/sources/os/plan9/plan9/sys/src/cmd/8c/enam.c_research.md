# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/enam.c

## Purpose
Defines `anames[]`, the printable names for every opcode in `enum as`.

## Key Contents
- String table beginning with `"XXX"`, `"AAA"`, `"AAD"`, etc.
- Covers integer, branch, stack, string, floating-point, pseudo-op, conditional move, and final `"LAST"` names.
- Names correspond by index to `enum as` in `8.out.h`.

## Important Behavior
- Used by formatters, diagnostics, listings, and debug output.
- Must remain synchronized with opcode enum order.
- Includes names for extra post-`AEND` pseudo and extended opcodes such as `DYNT`, `INIT`, `SIGNAME`, `FCOMI`, `CMPXCHG*`, `CMOV*`, and `FCMOV*`.

## Research Notes
This file has no algorithmic logic, but it is critical for human-readable assembly output and diagnostics.
