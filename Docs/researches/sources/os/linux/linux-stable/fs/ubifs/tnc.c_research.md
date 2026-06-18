# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc.c

## Purpose
Implements the UBIFS Tree Node Cache: lookup, mutation, collision resolution, leaf-node cache, bulk reads, deletion, GC membership checks, and dirtying of index nodes.

## Key Behavior
- TNC is a cached B-tree of index znodes protected by `c->tnc_mutex`.
- Old index nodes are tracked in `c->old_idx` RB-tree so crash recovery can keep the previous committed index intact until the new commit succeeds.
- Dirtying uses copy-on-write when a znode is part of an active commit (`COW_ZNODE`), preserving commit consistency while foreground mutations continue.
- Leaf-node cache (`zbr->leaf`) stores copied dirent/xattr leaf nodes for readdir and hash collision resolution.
- `ubifs_lookup_level0()` finds the level-0 znode and slot for a key, loading missing znodes from flash as needed.
- Hashed keys require extra collision resolution by full name (`resolve_collision()`), fallible replay-aware matching, direct location matching for GC moves, or double-hash cookie lookup.
- `ubifs_tnc_locate()` supports lock-dropping reads for non-hash keys, with GC sequence checks and safe retry if the LEB may have moved.
- Bulk-read support finds adjacent data nodes in one LEB, reads through write-buffer overlap when necessary, and validates every returned data node.
- Insertions split full znodes, update parent keys, and record altered old-index references when split/leftmost-key changes may make old nodes hard to find.
- Deletions remove branches, free LNC entries, add obsolete space to dirt, collapse empty znodes, and may collapse the root.
- Range, inode, xattr, and directory-entry removal APIs build on lookup/delete primitives.
- GC-facing APIs answer whether index or leaf nodes still belong to TNC and dirty index nodes before collection.

## Important Dependencies
- Uses znode load/read helpers from `tnc_misc.c`.
- Commit integration depends on `c->cnext`, `COW_ZNODE`, `DIRTY_ZNODE`, obsolete flags, dirty/clean counters, and old-index tracking.
- Uses UBIFS node read/hash validation, lprops dirt accounting, write-buffer reads, key comparison helpers, and fscrypt names.

## Invariants and Risks
- The main concurrency rule is simple but broad: tree traversal and mutation require `c->tnc_mutex`; selected read paths briefly drop it only with GC race detection.
- Hash collisions are first-class: duplicate keys are legal only for hashed dent/xent keys and must be disambiguated before mutation.
- During replay, dangling branches may exist because GC and unclean commits can leave references to nodes no longer on media; fallible matching handles this.
- Parent key correction is delicate because GC may need to find old index nodes by old key/address; the old-index RB-tree covers cases where lookup by key becomes unreliable.
- Clean znode counters intentionally interact with shrinker and commit accounting and may be temporarily inconsistent.
