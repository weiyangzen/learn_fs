# sources/object-store/daos/src/vos/vos_internal.h

## Purpose
`vos_internal.h` is the main private interface for the VOS implementation. It connects durable layout types to runtime pool/container/object state, DTX state, iterator contracts, record layout helpers, media allocation, timestamp conflict checks, aggregation flags, cache pinning, and cross-module prototypes.

## Important APIs and Types
The header defines tree orders, block constants, DTX local-id values, aggregation credit limits, metrics structures, and runtime `struct vos_pool`, `struct vos_container`, `struct vos_dtx_act_ent`, and `struct vos_dtx_cmt_ent`. It declares tree classes (`VOS_BTR_DKEY`, `AKEY`, `SINGV`, object/container/DTX/ilog tables), record helpers (`vos_rec_bundle`, `vos_svt_key`, `vos_krec_size`, `vos_irec_msize`, checksum accessors), iterator abstractions (`struct vos_iterator`, `struct vos_iter_info`, `struct vos_iter_ops`, `struct vos_obj_iter`), and reservation/publish functions implemented in `vos_io.c`.

## Control Flow and Integration
Most VOS C files include this header to share handles and conventions. Public handles are cookie-cast to `vos_pool`, `vos_container`, or `vos_iterator`. IO code uses it to create record bundles, reserve SCM/NVMe space, choose media, publish reservations, and update aggregation flags. Iterator code uses `vos_iter_ops`, nested tree fetch information, anchors, and flags. DTX code uses the active/committed entry wrappers and helper predicates. Object/key code uses tree preparation, release, punch, delete, and corruption marking prototypes.

## State and Persistence
The runtime structures point at durable `vos_pool_df`, `vos_cont_df`, `vos_obj_df`, `vos_krec_df`, and `vos_irec_df` records defined in `vos_layout.h`. `vos_pool` owns umem, feature flags, container tree handle, VEA state, dedup hash, metrics, GC state, checkpoint context, and reservation thresholds. `vos_container` owns object btree handle, DTX tables and lists, stable epoch boundaries, GC/aggregation/discard runtime state, timestamp index, allocation hints, and DTX reindex cursors. Inline helpers encode persistent DTX states and solo-DTX semantics by using reserved local-id bits.

## Dependencies
Dependencies include GURT list/hash, DAOS btree/LRU/common/server APIs, BIO, VOS public types, TLS, durable layout, ilog wrappers, and object cache declarations. The header also exposes integration points for GC, space accounting, checksum recalculation, WAL flushing, NVMe target health, md-on-SSD phase2 bucket pinning, and layout upgrade.

## Risks and Test Signals
Because this header centralizes private contracts, risks include ABI/layout drift between durable and runtime structures, misuse of handle cookie casts, stale DTX local-id interpretation, feature-bit collisions with btree/evtree flags, and media decisions that disagree with reservation or record metadata. Test signals should cover DTX committed/aborted/prepared interpretation including solo transactions, aggregation timestamp packing for HLC and non-HLC epochs, SCM versus NVMe media selection, gang single-value sizing, iterator state transitions, cache pinning with current DTX temporarily cleared, and md-on-SSD bucket allocation paths.
