# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/vfprintf.c

## Purpose
`vfprintf.c` is a compatibility fallback for platforms lacking native `vfprintf()`.

## Important APIs, Types, and Functions
It defines `vfprintf(iop, fmt, ap)` in old K&R style and uses `_doprnt()` to implement formatting.

## Control Flow
The function calls `_doprnt(fmt, ap, iop)` and returns `ferror(iop) ? EOF : 0`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the target `FILE` stream. Dependencies are legacy libc `_doprnt`, stdio, and varargs ABI. Risks are obsolete platform assumptions, nonstandard return semantics compared with modern `vfprintf`, and build conflicts if libc already provides the symbol. Test signals are successful fallback builds on target legacy systems and correct com_err formatted output.
