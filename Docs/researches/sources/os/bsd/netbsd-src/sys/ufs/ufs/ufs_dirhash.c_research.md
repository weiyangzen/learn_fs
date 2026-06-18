# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_dirhash.c

This file implements the UFS large-directory hash cache.

Key responsibilities:
- Builds per-directory hash tables from directory contents.
- Performs hashed lookup with fallback to linear lookup via `EJUSTRETURN`.
- Finds free directory space quickly using per-block free-space summaries.
- Tracks useful directory end for truncating trailing unused blocks.
- Updates hash state on directory entry add, remove, move, new block, and truncation.
- Provides optional consistency checks against real directory block contents.
- Recycles dirhash memory under configurable global memory limits.
- Exposes sysctls for min blocks, max memory, used memory, and checking.

Important behavior:
- Uses open addressing with `DIRHASH_EMPTY` and `DIRHASH_DEL`.
- Uses a score-based hybrid recency/frequency recycling algorithm.
- Avoids hashing old-format directories and small directories.
- If a hash is recycled, its structure may remain but `dh_hash` becomes NULL, causing callers to free/rebuild or fall back.
