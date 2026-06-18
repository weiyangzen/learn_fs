# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/Makefile

## Summary
Builds the `mdconfig` runtime utility and its manual page.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=mdconfig`.
- Links against `libutil` and `libgeom`.
- Enables tests via `HAS_TESTS` and conditionally descends into `tests` when `MK_TESTS` is enabled.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`; the utility depends on GEOM and md(4) control interfaces.
