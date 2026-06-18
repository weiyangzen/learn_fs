# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cw.c

Cache-worm device implementation. It layers a writable cache device over a worm/read-only backing device and manages copy-on-write state, dumps, cache metadata, recovery, and cw-specific console commands.

Important behavior:
- Cache entry states include `Cnone`, `Cdirty`, `Cdump`, `Cread`, `Cwrite`, `Cdump1`, and `Cerror`.
- `cwio()` is the core state machine for read/write/grow/dump/release/free operations.
- `dumpblock()` copies queued dump entries from cache to worm and updates cache entry state.
- `cwream()` initializes a fresh cache-worm filesystem with cache metadata, superblock, cw root, and ro root.
- `cwrecover()` rebuilds cache metadata from the latest valid worm superblock chain.
- `getcentry()` maps worm addresses to cache buckets and maintains age/resequence state.
- `cfsdump()` recursively snapshots dirty blocks, updates cw and ro roots, creates dated dump directory entries, writes a new superblock, rewrites cache metadata, and rewalks active fids.
- Console `cwcmd` subcommands inspect or mutate cache state, dump chains, cache warm-up files, superblocks, and accounting.
