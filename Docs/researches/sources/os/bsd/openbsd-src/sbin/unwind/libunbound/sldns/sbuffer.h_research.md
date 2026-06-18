# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.h

`sbuffer.h` defines `sldns_buffer`, a Java-NIO-style byte buffer with position, limit, capacity, data pointer, fixed/resizable flag, and sticky status-error flag.

It provides inline endian-safe integer helpers for unaligned network-order 16-bit, 32-bit, and 48-bit reads/writes. These are also used by raw DNS header and RR accessors elsewhere.

The inline buffer API covers invariants, clear/flip/rewind, position and limit management, capacity query, pointer access, remaining/available checks, raw byte writes, string writes, typed writes for 8/16/32/48-bit values, raw reads, and typed reads for 8/16/32-bit values. Most operations use assertions for bounds checking, so callers are expected to verify availability or reserve space first in production builds.

The declared non-inline API covers allocation, wrapping/copying data, resizing/reserving, formatted printing, freeing, and buffer copying. This header is the shared low-level byte-buffer abstraction used by the parser and wire conversion code.
