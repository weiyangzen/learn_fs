# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/Makefile.inc

OpenBSD make include for building the vendored/embedded Unbound sources used by `unwind`.

Behavior:
- Adds warning-oriented CFLAGS and includes `${.CURDIR}`.
- Sets `.PATH` to `${.CURDIR}/libunbound`.
- Includes component make fragments for dns64, iterator, libunbound, respip, services, cache, sldns, util, storage, and validator.

Role in group:
- Top-level build wiring for the `libunbound` subtree consumed by `sbin/unwind`.
