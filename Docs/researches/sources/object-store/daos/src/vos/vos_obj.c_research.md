# sources/object-store/daos/src/vos/vos_obj.c

## Purpose
`vos_obj.c` implements VOS object mutation, key/value iteration, object/key punch propagation, corruption marking, anchor conversion, and iterator operation tables for dkey, akey, single-value, and extent-value traversal. It sits above the object index/cache layer and below public VOS APIs and generic iterator orchestration.

## Important APIs, Types, And Functions
Key entry points include `vos_obj_punch`, `vos_obj_key2anchor`, `vos_obj_delete`, `vos_obj_delete_ent`, `vos_obj_del_key`, `vos_obj_mark_corruption`, `vos_obj_iter_prep`, nested iterator preparation/fetch helpers, and operation tables `vos_obj_dkey_iter_ops`, `vos_obj_akey_iter_ops`, `vos_obj_sv_iter_ops`, and `vos_obj_ev_iter_ops`. Internal helpers split by tree level: `key_punch`, `obj_punch`, `key_ilog_prepare`, `key_iter_fetch`, `singv_iter_*`, and `recx_iter_*`. The code depends on `struct vos_obj_iter`, `struct vos_krec_df`, `struct vos_rec_bundle`, ilog fetch state, evtree filters, and btree handles.

## Control Flow
Punch begins by validating dkey/akey constraints, allocating a timestamp set, acquiring the object, starting a VOS transaction, incarnating or finding the durable object, and then either punching the object ilog or walking into dkey/akey subtrees. `key_punch` records object/dkey/akey ilog punches and uses `vos_propagate_check` to collapse empty child trees upward. Iteration prepares the requested tree by holding the object, initializing the object tree, opening child btrees or evtree iterators, probing by anchor, checking ilog visibility, and filling `vos_iter_entry_t`. Nested iterators borrow parent context and avoid releasing parent-held objects unless they own the top-level dkey iterator.

## State And Persistence
Persistent state lives in object ilogs, key ilogs, btree roots, evtree roots, known-key offsets, corruption flags, and `vo_max_write`. Updates are transactional through `umem_tx_*` and VOS transaction wrappers; failed mutation paths evict object cache entries when necessary. Timestamp sets record read/write dependencies so uncertain creates, underpunches, and overlapping DTX activity return restart/in-progress errors rather than silently exposing ambiguous state.

## Dependencies And Integration Points
This file integrates with `vos_obj_cache.c` for object references, `vos_obj_index.c` for object ilog/persistent object records, key helpers, evtree, dbtree, VOS timestamp conflict detection, DTX commit helpers, media read/corruption marking, and generic VOS iteration. Scrubbing uses `VOS_ITER_PROC_OP_MARK_CORRUPT`, aggregation uses punch and aggregate process hooks, and query/fetch code depends on iterator output fields such as `ie_biov`, `ie_recx`, and checksums.

## Risks
The main risks are iterator lifetime mistakes around fake akeys and nested borrowed objects, stale anchor handling after aggregation, failure to propagate punches after child trees become empty, and subtle transaction restart requirements when timestamp uncertainty exists. The `obj_local`/cache transition and object eviction on punch/delete also require care because stale cached `obj_df` pointers would expose invalid persistent state. Single-value corruption marking mutates durable record address flags and must only run at a validated iterator position.

## Test Signals
Useful tests should cover object/dkey/akey punch with propagation, conditional punch nonexist behavior, underpunch restart behavior, nested iteration over normal and no-akey objects, reverse/forward extent iteration, fake akey anchors, aggregation delete/invisible return codes, corruption marking for SV and EV records, and races with discard/aggregation object flags.
