# sources/object-store/daos/src/vos/evt_iter.c

## Purpose
`evt_iter.c` implements evtree iterators for VOS extent trees. It prepares embedded or cloned iterator handles, probes first or matching extents, iterates forward/backward through visible/covered/raw records, fetches entries and anchors, deletes the current raw entry, and marks the current record corrupted for scrub/check paths.

## Important APIs, types, and functions
The exported APIs are `evt_iter_prepare`, `evt_iter_finish`, `evt_iter_probe`, `evt_iter_next`, `evt_iter_empty`, `evt_iter_delete`, `evt_iter_corrupt`, and `evt_iter_fetch`. Important helpers are `evt_validate_options`, `evt_iter_is_sorted`, `evt_iter_probe_sorted`, `evt_iter_probe_find`, `evt_iter_move`, `evt_iter_is_ready`, `evt_iter_intent`, `should_skip`, and `ent_array_reset`. It uses `struct evt_iterator`, `struct evt_context`, `struct evt_filter`, `struct evt_rect`, `struct evt_entry_array`, and `daos_anchor_t`.

## Control flow
`evt_iter_prepare` validates skip options, converts the tree handle to an `evt_context`, either reuses the embedded context iterator or clones the context, initializes default extent/epoch filters, direction, options, and state. Sorted iterators are used for visible or covered iteration and fill `it_entries`; raw iterators walk the tree trace directly.

`evt_iter_probe` resets the entry array, then either calls `evt_iter_probe_sorted` or performs a tree search using `EVT_FIND_FIRST`/`EVT_FIND_SAME`. Sorted probing fills all matching entries, sorts/filters by visibility, chooses first/last or binary-searches from an anchor rectangle, and skips unavailable or hole/data entries as requested. Raw probing fills the array for a first/same search, checks the current descriptor's DTX availability, and establishes READY or FINI state. `evt_iter_next` advances by array index or by `evt_move_trace`, honoring `it_skip_move` after deletion.

`evt_iter_fetch` validates READY state and copies either the sorted entry or the raw node entry into the caller's `evt_entry`, fills in bytes-per-record, and writes an anchor containing the current rectangle. `evt_iter_delete` is only supported for raw iterators; it optionally fetches the entry, starts a transaction, deletes the current leaf node entry, adjusts iterator state/trace, and avoids moving twice by setting `it_skip_move`. `evt_iter_corrupt` transactionally sets the current descriptor's bio address corrupted flag.

## State and persistence behavior
Iterator state is volatile in `tc_iter`: state enum, options, direction, index, filters, entry array, and trace position. Deletion and corruption are persistent mutations when the underlying `umem_instance` has transactions; they use `evt_tx_begin`, `umem_tx_add`, `evt_node_delete`, and `evt_tx_end`. Anchors serialize `struct evt_rect` into `daos_anchor_t`, so anchor compatibility is enforced with a compile-time size assert.

## Dependencies and integration points
The iterator depends on lower evtree primitives in `evt_priv.h` and sibling implementation files: context handle conversion, context cloning/refcounting, trace movement, entry-array fill/sort, descriptor availability checks, node/descriptor access, transaction helpers, and checksum/entry fill utilities. It is used by VOS query/object paths and heavily exercised by `src/vos/tests/evt_ctl.c`, including delete, anchor, visible, covered, and raw iteration cases.

## Risks and test signals
Risks include misuse of skip options, sharing embedded iterators across references, binary-search off-by-one errors for reverse anchors, stale anchors after aggregation/clipping returning the wrong error, skipping unavailable DTX records incorrectly for purge/discard/migration/check intents, and corrupt/delete transaction offset mistakes. Tests should cover visible and covered sorted iteration, reverse iteration, skip holes/data, anchor find returning `-DER_AGAIN` when raw records changed, raw delete of first/middle/last records, corruption marking, unavailable DTX filtering, and iterator finish/refcount cleanup.
