# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/dat.h

Central gefs data model, constants, on-disk layout notes, and shared structs.

Key contents:
- Defines block size, key/value limits, node layout sizes, message limits, cache sizes, and 9P/server table sizes.
- Defines B-tree key classes for data blocks, directory entries, parent links, snapshot labels, snapshot roots, deadlists, and config keys.
- Defines block types: data, pivot, leaf, log, deadlist, arena header/footer, and superblock.
- Defines mutation operations, wstat bit encodings, allocation-log operations, admin message operations, and deferred-free categories.
- Declares core structs: `Gefs`, `Arena`, `Tree`, `Blk`, `Bptr`, `Kvp`, `Msg`, `Dlist`, `Mount`, `Conn`, `Fid`, `Dent`, `Scan`, `Chan`, `User`, and `Trace`.

Role:
- Documents the disk format and provides the shared ABI between block I/O, B-tree logic, snapshot management, 9P serving, formatting, loading, and checking.
- Encodes gefs as a COW B-tree filesystem with arena allocation logs, snapshot chains, deadlists, block cache/LRU, deferred reclamation, and multiple worker queues.

Notable constraints:
- Block layout constants depend on `Blksz == 1<<14`.
- `Keymax`, `Inlmax`, `Msgmax`, and pivot-buffer sizing must satisfy assertions in `main.c`.
