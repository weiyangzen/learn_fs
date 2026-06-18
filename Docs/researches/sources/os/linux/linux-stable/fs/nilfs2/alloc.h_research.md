# File Research: sources/os/linux/linux-stable/fs/nilfs2/alloc.h

Purpose: declares NILFS2 persistent allocator APIs, request/cache structures, and bitmap helper aliases.

Key structures and state:
- `nilfs_palloc_entries_per_group()` computes entries per group as the number of bits representable by one bitmap block.
- `struct nilfs_palloc_req` holds an entry number and the descriptor/bitmap/entry buffer heads needed across prepare/commit/abort phases.
- Bitmap operations are aliased to ext2 atomic bit helpers and little-endian bit scanning helpers.
- `struct nilfs_bh_assoc` pairs a metadata block offset with a cached buffer head.
- `struct nilfs_palloc_cache` contains a spinlock and cached descriptor, bitmap, and entry block associations.

Major logic:
- Declares initialization, entry-block lookup, entry offset calculation, maximum-entry counting, allocation prepare/commit/abort, free prepare/commit/abort, vector free, and cache lifecycle functions.
- Defines the split transaction model used by callers that need to prepare metadata changes before committing them to the log.

Concurrency and lifetime:
- Request buffer heads are owned by callers between prepare and commit/abort.
- Cache buffer-head references are protected by `nilfs_palloc_cache.lock` and released on clear/destroy.

Important dependencies:
- Includes Linux types, buffer-head, and fs headers.
- Used by NILFS DAT, ifile, bmap, and metadata-file code.

Risk/edge cases:
- Callers must match every prepare with exactly one commit or abort to avoid leaked buffer references or stale bitmap changes.
- Entry offset calculations depend on metadata inode entry-size initialization.
