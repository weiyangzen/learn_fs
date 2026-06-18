# File Research: sources/os/bsd/openbsd-src/sys/sys/_endian.h

Purpose: Provides internal endian constants and byte-swap/conversion macros.

Key behavior:
- Includes machine endian definitions and normalizes `_LITTLE_ENDIAN`, `_BIG_ENDIAN`, `_PDP_ENDIAN`, and `_BYTE_ORDER` use.
- Defines generic 16/32/64-bit byte-swap expressions plus inline machine-default fallbacks.
- Chooses constant-folded swaps for compile-time constants and machine swaps otherwise.
- Defines host-to-big/little and big/little-to-host conversion macros depending on platform byte order.
- In kernel builds, provides memory-load/store endian helpers for big/little-endian packed memory, with machine-specific swap I/O hooks when available.
- Defines `_QUAD_HIGHWORD` and `_QUAD_LOWWORD` according to endian mode.

Filesystem relevance:
- Used by filesystem and block formats that need stable on-disk byte-order conversions independent of CPU endian.
