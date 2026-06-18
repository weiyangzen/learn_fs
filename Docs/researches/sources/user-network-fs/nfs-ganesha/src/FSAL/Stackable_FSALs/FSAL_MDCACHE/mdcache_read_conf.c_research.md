# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_read_conf.c

## Purpose
`mdcache_read_conf.c` defines the MDCACHE configuration block, defaults, validation, and post-parse derived parameters. It populates the global `mdcache_param` used by cache sizing, directory chunking, FD caching, LRU workers, dirmap limits, delegation heuristics, and owner-override behavior.

## Important APIs, Types, and Functions
- Global `struct mdcache_parameter mdcache_param` stores parsed configuration.
- `mdcache_params[]` maps config item names to struct fields with bounds and defaults, including `NParts`, `Cache_Size`, directory chunk settings, entry/chunk watermarks, LRU/FD reaper settings, `Dirmap_HWMark`, delegation percent, and cached owner override.
- `mdcache_param_init()` returns the singleton config target.
- `mdcache_param_commit()` validates that `Chunks_LWMark` does not exceed `Chunks_HWMark`.
- `mdcache_param_blk` registers the `MDCACHE` block with `CacheInode` as an alternate name.
- `mdcache_set_param_from_conf()` loads config, handles legacy `Dir_Chunk = 0`, computes `avl_chunk_split` and `avl_detached_max`, and derives `g_max_files_delegatable`.

## Control Flow
During startup, `load_config_from_parse()` fills `mdcache_param` from the parse tree and invokes commit validation. After successful parse, legacy directory-chunk disablement is normalized into the newer enable flag, chunk split threshold is computed as 1.5 times chunk size rounded to an even value, detached dirent capacity is computed from chunk size and multiplier, and the global delegation cap is computed from the configured percentage of `Entries_HWMark`.

## State and Persistence Behavior
Configuration is process-global and in-memory. It is loaded at startup/config processing time and consumed by LRU initialization, directory caching, FD caching, and delegation logic. No runtime persistence is performed.

## Dependencies and Integration Points
This file depends on config parsing infrastructure, `mdcache_int.h`/`mdcache_ext.h` for parameter definitions, logging, and global delegation state. Its outputs are consumed by `mdcache_lru.c`, `mdcache_helpers.c`, and other MDCACHE access/delegation paths.

## Risks and Edge Cases
Risk centers on invalid or surprising parameter interactions: low chunk watermark above high watermark is rejected, but equal values are allowed; very large chunk/detached settings can increase memory pressure; `Entries_Release_Size = 0` disables entry release attempts; legacy `Dir_Chunk = 0` changes two fields; and delegation percentage directly scales with the entry high-water mark.

## Test Signals
Test parse defaults, legacy `Dir_Chunk = 0`, invalid chunk low/high ordering, bounds on each config item, computed `avl_chunk_split` and `avl_detached_max`, DBus block naming, and resulting `g_max_files_delegatable` for boundary percentages and high-water marks.
