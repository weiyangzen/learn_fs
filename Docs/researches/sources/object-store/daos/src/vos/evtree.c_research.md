# sources/object-store/daos/src/vos/evtree.c

## Purpose
Implements DAOS VOS epoch/extent tree storage for versioned array-value extents. It stores rectangles keyed by logical extent plus major/minor epoch, tracks persistent `umem` nodes/descriptors, finds visible data for reads/iteration, inserts overwrites or punches, deletes exact records, drains/destroys trees, and maintains checksum metadata attached to extent descriptors.

## Important APIs, Types, And Functions
Public entry points include `evt_create`, `evt_open`, `evt_close`, `evt_destroy`, `evt_insert`, `evt_find`, `evt_delete`, `evt_remove_all`, `evt_drain`, `evt_debug`, `evt_has_data`, `evt_feats_set`, checksum helpers, and overhead/validation helpers. Internal flow is organized around `struct evt_context`, `struct evt_trace`, policy ops (`evt_soff_pol_ops`, `evt_sdist_pol_ops`, `evt_sdist_even_pol_ops`), durable `struct evt_root`, persistent `struct evt_node`, `struct evt_node_entry`, and `struct evt_desc`. `evt_ent_array_fill` and `evt_ent_array_sort` are central to query results and visibility calculation.

## Control Flow
Creation initializes a context, selects a tree policy from feature bits, initializes the root in a transaction, and returns a handle. Insert first probes for same-epoch overwrite/uncertainty, then begins a transaction, activates an empty root if needed, and calls `evt_insert_entry`. Tree descent chooses the child with the smallest MBR weight growth; `evt_insert_or_split` inserts into a leaf or splits nodes upward, possibly creating a new root. Finds traverse MBRs with `evt_filter_rect`, overlap checks, DTX availability callbacks, and then sort/split candidates to produce visible extents. Removal inserts hole/removal records for visible ranges; exact delete locates one record and bubbles node removal/MBR updates upward.

## State And Persistence
Persistent state is in the caller-owned root and `umem` allocated nodes/descriptors. Mutations use `evt_tx_begin`, `evt_root_tx_add`, `evt_node_tx_add`, `umem_tx_add_ptr`, `vos_obj_alloc`, and `umem_free`. The tree stores fixed `tr_inob`, checksum configuration, feature bits, order/max order, depth, pool UUID, and root node offset. Descriptors persist bio addresses, checksums, versions, and DTX state through callbacks.

## Dependencies And Integration
Depends on `evt_priv.h`, DAOS checksum helpers, VOS object allocation, `umem`, bio address semantics, DTX availability/log callbacks, and VOS tree callers in `vos_tree.c`/`vos_io.c`. Policy operations isolate sort/split behavior from generic tree mutation.

## Risks
The implementation is transaction-sensitive and relies on trace correctness across splits/deletes. Same-epoch partial overwrite is intentionally rejected. Large non-hole extents above durable length encoding are rejected; large hole insertion is decomposed through a query pass. Visibility splitting can allocate up to a computed upper bound and returns `-DER_AGAIN` on reallocation to restart safely. Data-loss handling depends on `evt_desc_log_status` returning `-DER_DATA_LOSS`. Source has suspicious duplicated lines in a few places, so future edits should compile-check carefully.

## Test Signals
Direct tests are not in this subset. Integration signals are DAOS VOS tests (`run_ilog_tests` and broader VOS suites), VOS IO paths that call `evt_find`/checksum helpers, and storage estimator tests that model related VOS structure overhead. High-value tests are insert/find visibility overlap cases, same-epoch overwrite rejection, hole/removal aggregation, checksum slicing, node split/delete, DTX unavailable/data-loss statuses, and dynamic-root order growth.
