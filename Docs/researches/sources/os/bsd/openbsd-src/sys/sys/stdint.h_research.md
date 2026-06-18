# File Research: sources/os/bsd/openbsd-src/sys/sys/stdint.h

Standard fixed-width integer type and limit definitions.

This header maps OpenBSD machine types to C99 integer typedefs: exact-width, least-width, fast-width, pointer-capable, and maximum-width integer types. It defines min/max constants for those types, pointer difference limits, `sig_atomic_t`, `size_t`, wide-character and wide-int limits, and integer constant construction macros.

It handles 32-bit versus 64-bit pointer-size limits through `__LP64__` and uses compiler-provided fast-width limits.

Filesystem/storage relevance: foundational. Filesystem metadata, block counts, offsets, device ids, ABI structs, and serialization code depend on stable integer widths and limits.
