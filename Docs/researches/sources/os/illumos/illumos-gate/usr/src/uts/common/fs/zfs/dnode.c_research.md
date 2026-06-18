# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dnode.c

## Purpose

Implements in-core dnode lifecycle and open-context dnode operations: cache construction/destruction, byteswapping, allocation/reallocation, movable dnode support, dnode handle/slot management, object lookup and claiming, dirty marking, block-size and indirection changes, range-free tracking, used-space accounting, dbuf eviction, and sparse/hole/data scanning.

## Main Entry Points

- `dnode_init()` / `dnode_fini()`: create/destroy the `dnode_t` kmem cache and dnode kstats.
- `dnode_allocate()`, `dnode_reallocate()`, `dnode_free()`: allocate, reshape, or mark dnodes for freeing.
- `dnode_hold_impl()`, `dnode_hold()`, `dnode_try_claim()`, `dnode_add_ref()`, `dnode_rele()`: find, instantiate, claim, reference, and release dnodes.
- `dnode_setdirty()`: place a dnode on the objset dirty list and dirty its containing dbuf.
- `dnode_set_blksz()`, `dnode_set_nlevels()`, `dnode_new_blkid()`: update block geometry and top-level indirection state.
- `dnode_free_range()`, `dnode_block_freed()`: record block ranges to free in the syncing phase and query recent frees.
- `dnode_evict_dbufs()`, `dnode_evict_bonus()`: evict cached dbufs for a dnode.
- `dnode_next_offset()`: find next/previous hole, data, or sparse dnode-region offset.

## Control Flow And State

The file separates persistent `dnode_phys_t` from mutable in-core `dnode_t`. `dnode_create()` copies geometry/type/checksum/compression/bonus/spill state from disk, initializes zfetch, links regular objects into `os_dnodes`, and then publishes `dn_objset` as the final step so the kernel dnode-move callback sees only fully initialized dnodes. `dnode_destroy()` invalidates the pointer, unlinks from the objset, destroys bonus/zfetch state, handles objset eviction completion, and returns ARC metadata space.

Dnode slots are tracked per dnode block using `dnode_children_t` and one `dnode_handle_t` per slot. Handles can be `DN_SLOT_FREE`, `DN_SLOT_ALLOCATED`, `DN_SLOT_INTERIOR`, `DN_SLOT_UNINIT`, or an actual dnode pointer. `dnode_hold_impl()` initializes this state from the meta-dnode block, handles multi-slot dnodes, supports dry-run free claims, rejects interior-slot lookups, and carefully coordinates handle locks with the parent dbuf reference so instantiated dnodes cannot move or disappear.

Dirty state is txg-indexed. Open-context mutations store pending next values in `dn_next_*[txg & TXG_MASK]` and dirty the dnode for later syncing. Range frees are recorded in `dn_free_ranges[]` as block-id range trees after partial head/tail blocks are zeroed and relevant level-1 indirect dbufs are dirtied. This lets open context mark intent while syncing context later mutates block pointers and frees space.

`dnode_next_offset()` climbs up and down the block tree using fill counts to locate matching holes/data, with special handling for meta-dnode object allocation scans and the virtual hole at object end. It reads indirect blocks with `DB_RF_NO_DECRYPT` because dnode metadata inspection does not require decrypted payload.

The kernel-only dnode move path allows kmem to relocate inactive dnodes. It holds objset and dnode-handle locks, verifies active holds are no more than dbuf-owned holds, transfers dirty records, dbuf AVL entries, zfetch streams, handles, and back-pointers, then invalidates the old object.

## Dependencies

Depends on dbuf cache internals, dmu objset state, txg-indexed dirty lists, range trees, zfetch, ARC space accounting, SPA feature limits for large dnodes and block sizes, user/group/project accounting helpers, and zrl locks used by dnode handles.

## Risks

This is one of the most delicate files in the ZFS DMU. Correctness depends on exact ordering between dnode holds, parent dbuf holds, handle locks, dbuf AVL mutations, and dirty-list membership. Multi-slot dnode allocation must keep interior slots consistent with on-disk `dn_extra_slots`. Range-free tracking must dirty enough indirect metadata without instantiating dbufs that `dbuf_free_range()` assumes absent. Dnode moving is particularly sensitive to stale back-pointers and active reference misclassification.
