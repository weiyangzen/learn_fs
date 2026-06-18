# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap.h

This header wraps byte-swap macro definitions.

Core contents:
- Includes `byteswap1.h`.
- Defines `bswap_16`, `bswap_32`, and under GCC 2+ `bswap_64` as macro aliases to internal implementations.

Risk points:
- It is a glibc-derived compatibility header.
- It must be paired with `byteswap1.h`; direct architecture assumptions live there.
