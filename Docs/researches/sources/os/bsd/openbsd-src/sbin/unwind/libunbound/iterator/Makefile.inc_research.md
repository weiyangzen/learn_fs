# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/Makefile.inc

Build fragment for Unbound iterator module sources.

Behavior:
- Adds `.PATH` for `libunbound/iterator`.
- Adds iterator-related source files to `SRCS`, including delegation points, do-not-query, forward zones, hints, private address handling, response typing, scrub logic, utilities, and main iterator.

Role in group:
- Wires iterator support into the embedded Unbound build.
