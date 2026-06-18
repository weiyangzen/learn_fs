# File Research: sources/os/bsd/dragonflybsd/sys/sys/endian.h

`endian.h` provides generic endian conversion and unaligned byte-stream encode/decode helpers. It includes `sys/types.h` and `machine/endian.h`.

It defines `_QUAD_HIGHWORD`/`_QUAD_LOWWORD`, `bswap16/32/64`, host-to-big/little and big/little-to-host conversion macros, and inline `be16/32/64dec`, `le16/32/64dec`, `be16/32/64enc`, and `le16/32/64enc`.

The encode/decode helpers operate byte-by-byte, so they are alignment-agnostic and suitable for disk/network formats.
