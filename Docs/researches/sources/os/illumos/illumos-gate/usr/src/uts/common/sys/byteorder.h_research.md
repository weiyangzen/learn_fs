# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/byteorder.h

This header provides host/network and explicit endian conversion support. On big-endian builds, `ntohl`/`htonl`/related macros are identity operations; otherwise functions/prototypes and byte-swap macros handle conversion. It also defines `in_port_t` and `in_addr_t` if not already defined.

It exposes `BSWAP_*`, `BMASK_*`, `BE_*`, `LE_*`, and unaligned-safe load/store macros (`BE_IN*`, `LE_IN*`, `BE_OUT*`, `LE_OUT*`) with architecture-specific optimizations when `_ASM_INLINES` is available.
