# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2.c

MD2 implementation derived from RFC 1319, compiled only when `HAVE_MD2_H` is false.

Main APIs:
- `MD2Init`
- `MD2Update`
- `MD2Final`
- `MD2Transform`

Core data:
- RFC 1319 substitution table `S[256]`.
- Padding table for 1..16 byte MD2 padding.

Behavior:
- `MD2Transform` updates checksum and mangles the 48-byte internal block state.
- `MD2Update` appends input into context block space and transforms full blocks.
- `MD2Final` pads, appends checksum, copies 16-byte digest, and resets context.
- Weak aliases expose public names to internal underscored implementations.

Dependencies: `<md2.h>`, `namespace.h`, optional `nbtool_config.h`.
