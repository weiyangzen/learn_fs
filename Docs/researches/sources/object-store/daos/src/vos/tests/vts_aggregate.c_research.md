# sources/object-store/daos/src/vos/tests/vts_aggregate.c

## Purpose

`vts_aggregate.c` is the main cmocka coverage for VOS aggregation and discard behavior. It builds synthetic single-value and extent-value histories, runs `vos_aggregate()` or `vos_discard()` over chosen epoch ranges, and verifies both the visible logical value and, where deterministic, the number of surviving physical records. It also covers checksum aggregation, object/key punches, delete records, NVMe merge selection, flat dkey object layouts, and aggregation timestamp encoding.

## Important APIs, Types, And Functions

The file exports `run_discard_tests()` and `run_aggregate_tests()`. Its central test model is `struct agg_tst_dataset`, which records the OID/type, update epoch range, aggregation/discard epoch range, recx layout, expected view buffer, expected physical record count, and flags for discard/delete behavior.

`update_value()` and `fetch_value()` wrap the common VOS I/O helpers from `vts_io.h`, constructing dkeys, akeys, `daos_iod_t`, and `d_sg_list_t`. They also toggle test flags such as `TF_PUNCH`, `TF_DELETE`, `TF_USE_VAL`, `TF_USE_CSUMS`, and occasionally `TF_ZERO_COPY`. `phy_recs_nr()` uses `vos_iterate()` with `VOS_ITER_SINGLE` or `VOS_ITER_RECX` to count physical entries. `generate_view()` captures the logical value expected before compaction, while `verify_view()` checks post-aggregation fetch results and physical record counts.

`aggregate_basic_lb()` is the core driver: it writes one update per epoch, optionally injects punches/deletes, snapshots the expected value, runs `vos_discard()` or `vos_aggregate()`, then verifies. `aggregate_multi()` applies randomized workloads across multiple objects, dkeys, and akeys. The punch helpers (`do_punch()`, `agg_punches_test_helper()`) exercise object, dkey, and akey punches. `removal_stress_case()` drives complicated delete-record compaction patterns.

## Control Flow

The cmocka arrays split discard cases (`VOS451`-`VOS469`) from aggregate cases (`VOS401`-`VOS437`). Most tests create a dataset, populate epoch/record shape, and call a shared driver. SV tests vary confined epoch ranges, full-range cleanup, random punch/yield, and multiple-key workloads. EV tests vary disjoint, adjacent, overlapping, fully covered, merge-window-spanning, random, checksum, and delete-record scenarios.

Longer tests include `aggregate_14()`, which repeatedly fills a pool and aggregates to observe storage recovery, and `aggregate_34()`, which skips when NVMe is unavailable and compares scan-only versus force-merge behavior. `aggregate_35()` is a pure unit test for `vos_feats_agg_time_get()` and `vos_feats_agg_time_update()`.

## State And Persistence Behavior

The suite deliberately creates persistent VOS pool/container state via the shared I/O fixture, mutates records across epochs, and then checks that aggregation/discard only changes physical representation where allowed. Full-range discard expects object disappearance via `lookup_object()`. Repeated update/aggregate tests query pool space before and after aggregation. Fail locations such as `DAOS_VOS_AGG_RANDOM_YIELD` and `DAOS_VOS_AGG_MW_THRESH` force scheduler-yield and merge-window paths.

## Dependencies And Integration Points

The file depends on `vts_io.h`, VOS internals, container server definitions, cmocka assertions, DAOS dkey/akey helpers, VOS object/update/fetch/punch APIs, VOS iterators, fail injection, GC waiting, and pool query/stat structures. It integrates directly with the test runner through `setup_io()` and `teardown_io()`.

## Risks And Test Signals

The highest-risk areas are randomized workloads, fail-injection-dependent paths, large pool fills, and assumptions about physical record counts after compaction. Some expected counts are intentionally `-1` when physical layout is nondeterministic. `aggregate_22()` also protects conditional fetch/update semantics across aggregation. Passing signals include stable logical fetches before/after compaction, expected object nonexistence after full discard, no infinite iterator loop, checksum-safe aggregation, and correct timestamp feature encoding.
