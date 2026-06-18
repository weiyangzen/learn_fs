# File Research: sources/os/bsd/netbsd-src/sys/sys/endian.h

Defines byte-order constants, host/network conversion interfaces, host-to/from endian macros, and unaligned endian encode/decode helpers.

Key content:
- `_LITTLE_ENDIAN`, `_BIG_ENDIAN`, `_PDP_ENDIAN`.
- Feature-gated typedefs for `in_addr_t`, `in_port_t` and declarations for `htonl`, `htons`, `ntohl`, `ntohs`.
- Includes machine endian and bswap headers.
- Defines `_QUAD_HIGHWORD`/`_QUAD_LOWWORD`.
- XOpen/NetBSD traditional `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, `BYTE_ORDER`.
- Network conversion macros optimized for native big-endian or bswap otherwise.
- `htobe*`, `htole*`, `be*toh`, `le*toh` and in-place uppercase variants.
- NetBSD-source endian stream helpers: `be16enc/dec`, `be32enc/dec`, `be64enc/dec`, `le16enc/dec`, `le32enc/dec`, `le64enc/dec`.

Important behavior:
- Uses builtin memcpy-based helpers when supported to avoid alignment issues; otherwise falls back to byte-wise encoding/decoding.
- Namespace exposure depends on feature-test macros.
