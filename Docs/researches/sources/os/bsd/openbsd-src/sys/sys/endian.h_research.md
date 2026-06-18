# File Research: sources/os/bsd/openbsd-src/sys/sys/endian.h

This header exposes public endian and byte-swap conversion macros.

Key definitions:
- Public aliases: `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, `BYTE_ORDER`.
- Host/endian conversion macros: `htobe16/32/64`, `htole16/32/64`, `be16/32/64toh`, `le16/32/64toh`.
- BSD-visible helpers: `swap16/32/64`, `swap16_multi`, `betoh*`, `letoh*`, `htons`, `htonl`, `ntohs`, `ntohl`, `NTOH*`, `HTON*`.
- Kernel memory conversion aliases: `bemtoh*`, `htobem*`, `lemtoh*`, `htolem*`.

Behavior and integration:
- Includes `<sys/cdefs.h>` and `<sys/_endian.h>`.
- Public userspace should include `<endian.h>`; kernel code should include `<sys/endian.h>`.

Risk notes:
- `be*toh` and `betoh*` intentionally map to the same low-level `__htobe*` transformations because swaps are symmetric.
- BSD-visible socket byte-order macros are only defined if not already provided.
