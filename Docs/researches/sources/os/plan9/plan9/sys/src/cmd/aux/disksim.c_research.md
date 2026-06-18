# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/disksim.c

This file implements a synthetic disk device filesystem resembling `/dev/sdXX`.

Key behavior:
- Exposes a root directory containing an `sdXX` directory, with `ctl` and partition files underneath.
- `ctl` reads print inquiry, geometry, and partition table data.
- `ctl` writes accept `part`, `delpart`, `inquiry`, and `geometry` commands.
- Partition files support bounded reads and writes over sparse in-memory block storage.
- Can back storage with a real file, reading blocks lazily and writing dirty blocks back unless read-only.

Important details:
- Uses 8192-byte blocks and triple-indirect pointer tables for sparse addressing.
- Default partition is `data`.
- Partition qid versions change on replacement to catch stale fids.
- Supports service posting, mount point selection, read-only mode, and debug 9P logging.

Filesystem relevance:
- Direct: user-level simulated block-storage namespace with dynamic partitions.
