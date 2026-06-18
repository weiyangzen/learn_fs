# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zap_micro.c

## Role
Provides public ZAP APIs and the micro-ZAP implementation. It handles name hashing/normalization, micro-ZAP AVL indexing, object creation/destruction, locking, micro-to-fat upgrade, lookup/add/update/remove wrappers, cursor serialization, and stats.

## Hashing And Names
- `zap_getflags()`, `zap_hashbits()`, and `zap_maxcd()` derive hash/collision behavior from fat-ZAP flags.
- `zap_hash()` uses prehashed uint64 keys when requested or salted CRC64 over normalized string/uint64 key data, keeping only high hash bits.
- `zap_normalize()` applies Unicode text preparation for case/form insensitive matching.
- `zap_name_alloc()` creates string-key descriptors with original and normalized keys; case-sensitive matching on mixed/insensitive datasets adjusts normalization flags.
- `zap_name_alloc_uint64()` creates uint64-key descriptors and requires no normalization.

## Micro-ZAP Internals
- Micro-ZAP stores fixed entries with name, 64-bit value, hash, and collision differentiator.
- `mzap_open()` builds or reuses a `zap_t` from a dbuf and, for micro-ZAP, constructs an AVL tree over populated entries for lookup order.
- `mze_insert()`, `mze_find()`, `mze_find_unused_cd()`, `mze_remove()`, and `mze_destroy()` manage in-memory micro entry indexing.
- `mzap_addent()` finds a free physical slot, fills value/name/CD, updates allocation cursor and count, and inserts into AVL.
- `mzap_normalization_conflict()` checks neighboring entries with the same hash for normalized-name conflicts.

## Locking And Upgrade
- `zap_lockdir_impl()` consumes a held dbuf, interns/opens the ZAP, chooses lock mode based on micro/fat and `fatreader`, dirties on writer locks, expands micro block size until `MZAP_MAX_BLKSZ`, and upgrades to fat if needed.
- `zap_unlockdir()` releases the rwlock and dbuf hold.
- `mzap_upgrade()` copies the micro block, destroys the AVL, calls `fzap_upgrade()`, and re-adds all micro entries to the fat ZAP preserving CDs.
- Fat-only flags force immediate upgrade in `mzap_create_impl()`.

## Public Creation And Destruction
- `zap_create*()` and `zap_create_claim*()` allocate or claim DMU objects, then initialize micro-ZAP state with salt and normalization flags.
- `zap_create_flags*()` sets explicit block sizes and creates a fat-capable object with flags.
- `zap_destroy()` delegates to `dmu_object_free()`.
- `zap_evict_sync()` destroys the ZAP rwlock and either micro AVL or fat entry mutex.

## Public Operations
- `zap_count()` returns micro count or fat count.
- `zap_lookup*()` variants support normal, normalized, dnode, and uint64-key lookup paths.
- `zap_contains()` treats `EOVERFLOW`/`EINVAL` from zero-length reads as found.
- `zap_length*()` reports stored integer size/count.
- `zap_add*()` uses micro storage when possible; upgrades to fat for non-8-byte values, multi-integer values, long names, full objects, or uint64-key APIs.
- `zap_update*()` updates in place for micro-compatible entries or upgrades and delegates to fat update.
- `zap_remove*()` removes from micro or fat; normalized and dnode variants are supported.

## Cursor And Stats
- `zap_cursor_init*()` records object, serialized cursor, and prefetch preference.
- `zap_cursor_retrieve()` lazily locks the ZAP, decodes serialized `(hash, cd)`, then retrieves from fat cursor code or micro AVL.
- `zap_cursor_serialize()` packs high hash bits and collision differentiator for resumable iteration, preserving 32-bit-friendly cursors when possible.
- `zap_cursor_advance()` increments CD.
- `zap_cursor_fini()` releases retained ZAP and leaf references.
- `zap_get_stats()` reports micro summary or delegates to fat stats.

## Important Details
- Lua-like or userland callers are not involved here; this is the kernel ZAP API used broadly by ZFS metadata.
- Micro-ZAP only stores 64-bit scalar values and short names; any richer value shape converts to fat ZAP.
- Serialized cursor corruption is tolerated by resetting an out-of-range CD to 0.
- The dbuf user object is shared and raced via winner logic so multiple openers converge on one `zap_t`.
