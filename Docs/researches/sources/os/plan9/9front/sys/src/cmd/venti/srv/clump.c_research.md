# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/clump.c

Implements clump storage and loading: Venti’s immutable content block format inside arenas.

Key behavior:
- `storeclump` validates lump size/type, prepares a `Clump`, compresses with `whackblock` when useful, writes through `writeiclump`, and fills returned `IAddr`.
- Stored data layout is `Clump` header followed by compressed or raw data and four zero bytes.
- `clumpmagic` reads and unpacks the magic at an arena offset.
- `loadclump` reads enough arena data for a clump, unpacks the header, rejects `VtCorruptType`, reads more data if the initial block estimate was too short, decompresses if needed, and optionally verifies SHA-1 and type.

Interactions:
- Uses `whack.h` compression/decompression.
- Uses `readarena`, `writeiclump`, `pack/unpackclump`, and score helpers.
- Called from request lookup/debug paths and write path.

Notable details:
- For uncompressed clumps it computes a pre-copy SHA-1 and records an error if wrong, then copies data; final verification is controlled by `verify`.
- `blocks` is treated as a rough I/O estimate and raised to at least 1.
