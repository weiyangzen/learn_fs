# sources/object-store/daos/src/vos/vos_iterator.c

## Purpose
`vos_iterator.c` implements the generic iterator front end for VOS containers, objects, dkeys, akeys, single values, recx entries, and DTX records. It dispatches to per-type iterator operation tables, manages nested iterators, anchors, recursive traversal, timestamp read sets, scheduler-yield revalidation, and callback action semantics.

## Important APIs and Functions
Public APIs are `vos_iter_type2name`, `vos_iter_prepare`, `vos_iter_finish`, `vos_iter_validate`, `vos_iter_probe_ex`, `vos_iter_probe`, `vos_iter_next`, `vos_iter_fetch`, `vos_iter_copy`, `vos_iter_process`, `vos_iter_empty`, `vos_iterate_key`, `vos_iterate_obj`, and `vos_iterate`. Internal helpers include `nested_prepare`, `is_sysdb_pool`, `iter_decref`, `vos_iter_ts_set_update`, `vos_iter_validate_internal`, `type2anchor`, `reset_anchors`, `set_reprobe`, `need_reprobe`, `advance_stage`, and `vos_iterate_internal`.

## Control Flow
`vos_iter_prepare` validates handles, chooses the dictionary entry for the iterator type, allocates an appropriate timestamp set for transactional reads, installs the active DTX handle, and calls the type-specific prepare op. Nested preparation first fetches child tree information from the parent cursor and then calls child `iop_nested_prepare`, incrementing the parent refcount. Probe, next, fetch, copy, process, and empty all verify iterator state and delegate to type-specific ops.

Recursive iteration is a staged state machine: probe, fetch current entry, optional pre callback, optional recursion into the child type, optional post callback, and next. Callback actions can skip, delete, yield, restart, abort, or exit. Anchors and reprobe flags preserve progress after deletion or yield. Scheduler sequence changes trigger yield detection and may revalidate parent iterator chains before continuing.

## State and Persistence
Iterator state is transient. `struct vos_iterator` stores type, ops, parent, DTX handle, timestamp set, flags, state, anchors, and refcount. Anchors persist caller-visible traversal position across calls. No durable state is written by the generic iterator front end itself, but `iop_process` callbacks may delete or aggregate entries through type-specific implementations. Timestamp sets are updated on successful iteration in transactional contexts.

## Dependencies and Integration
The file depends on the iterator operation tables declared in `vos_internal.h` and implemented by object/container/DTX iterator modules. It integrates with DTX TLS via `vos_dth_get/set`, VOS scheduler sequence checks, public `vos_iter_param_t`, `vos_iter_entry_t`, and `vos_iter_anchors`, md-on-SSD evictable bucket iteration, and key-tree iteration via `VOS_IT_KEY_TREE`.

## Risks and Test Signals
Risks include stale anchors after deletion, missing reprobe after yield, parent iterator use-after-free, incorrect timestamp conflict updates, nested iterator preparation before probing the parent, and recursive traversal resuming at the wrong level after revalidation. Tests should cover standalone and nested iterators, all supported iterator types, recursive object-to-record walks, pre/post callback actions, deletion during iteration, scheduler-yield revalidation, transactional read timestamp restart behavior, `vos_iterate_key` on open tree handles, and md-on-SSD bucket iteration with skipped buckets.
