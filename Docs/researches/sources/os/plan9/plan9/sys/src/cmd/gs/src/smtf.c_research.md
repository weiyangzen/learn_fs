# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.c

Move-to-front encode/decode stream filters.

Key behavior:
- `s_MTF_init` initializes the 256-byte symbol list in identity order.
- `s_MTFE_process` encodes each input byte as its current index, shifting preceding entries toward the byte’s previous position.
- `s_MTFD_process` decodes indexes back to bytes, optimized for frequent zero indexes and caching the first four entries in local variables.
- Decode has additional optimized paths for small indexes and long-sized chunk shifting for larger indexes.

Notable dependencies:
- State definition from `smtf.h`.
- Architecture constants for endian and long size.

Research notes:
- The comment notes zeros dominate in the BWBS code, motivating the decode fast path.
- Decode template provides `s_MTF_init` as reinitialization.
