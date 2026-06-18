# sources/object-store/daos/src/vos/vos_ilog.c

## Purpose
`vos_ilog.c` adapts the generic DAOS incarnation-log implementation to VOS semantics. It translates ilog entry transaction ids through VOS DTX state, parses creation and punch history into `struct vos_ilog_info`, and exposes update, punch, aggregation, discard, corruption, and timestamp-cache helpers used by object, dkey, and akey paths.

## Important APIs and Functions
Key public entry points are `vos_ilog_fetch_`, `vos_ilog_update_`, `vos_ilog_punch_`, `vos_ilog_set_flags_`, `vos_ilog_check_`, `vos_ilog_aggregate`, `vos_ilog_is_punched`, and the fetch lifecycle helpers. Callback glue in `vos_ilog_desc_cbs_init` binds `ilog` to `vos_dtx_check_availability`, `vos_dtx_register_record`, and `vos_dtx_deregister_record`. `vos_parse_ilog` is the central parser: it walks fetched ilog entries in reverse, handles committed, uncommitted, removed, and in-progress entries, tracks parent or passed-in punches, and derives `ii_create`, `ii_prior_punch`, `ii_prior_any_punch`, `ii_next_punch`, `ii_uncertain_create`, `ii_empty`, and `ii_full_scan`.

## Control Flow
Fetch opens with `ilog_fetch`, initializes `vos_ilog_info`, imports parent punch state when nested under an object or dkey, then parses entries against the requested epoch range and uncertainty bound. Update first fetches the log for conditional or conflict checks, rejects insert/update conditions when visibility does not match, opens the ilog, then calls `ilog_update` with the current DTX operation sequence as minor epoch. Punch is similar, but can no-op for non-leaf non-conditional punches, can reject conditional punches on nonexistent entities, and writes a punch entry only at the leaf. Aggregation calls generic `ilog_aggregate` and then refetches to expose the post-aggregation view.

## State and Persistence
The durable state is `struct ilog_df` stored in object/key records. DTX coupling is persistent through local DTX ids recorded in ilog entries. Minor epochs order sub-operations within an epoch; replay punches use a slightly lower minor epoch so later same-epoch updates can remain visible. Corrupted ilogs are blocked for normal access by `vos_ilog_failout` but remain available to discard, mark, kill, and check intents. Timestamp helpers map ilog roots into the VOS timestamp cache for conflict detection.

## Dependencies and Integration
This file depends on `vos_internal.h`, generic `ilog`, VOS DTX tables, timestamp sets, and epoch/punch helpers. It is called by object/key code and by `vos_io.c` when checking or changing object, dkey, and akey incarnations. Aggregation and discard use `vos_ilog_aggregate` and `vos_ilog_is_punched` to decide if logs and their owning records can be removed.

## Risks and Test Signals
Important risks are incorrect parent punch propagation, treating uncommitted entries as visible, mishandling uncertainty bounds, and corrupting DTX record registration on ilog add/delete. Tests should exercise conditional insert/update/punch, same-epoch minor ordering, DTX in-progress and aborted states, replay punches, parent punch coverage across object/dkey/akey levels, aggregation discard of committed and uncommitted entries, and corrupted-ilog failout behavior.
