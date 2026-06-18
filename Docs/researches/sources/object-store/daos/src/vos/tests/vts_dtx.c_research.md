# sources/object-store/daos/src/vos/tests/vts_dtx.c

## Purpose

`vts_dtx.c` tests distributed transaction visibility and bookkeeping in VOS. It covers prepared/committed/aborted DTX records, punch visibility, committed/aborted idempotence, committable cache behavior, iteration visibility, and DTX aggregation.

## Important APIs, Types, And Functions

`vts_init_dte()` builds a minimal `dtx_entry` with one target membership and a unique XID. `vts_dtx_begin()` allocates a `struct dtx_handle`, fills leader fields, initializes share lists, reserves DTX state, and attaches it with `vos_dtx_attach()`. `vts_dtx_end()` frees share peers, finalizes reserved state, detaches, and frees memory.

`vts_dtx_prep_update()` prepares common key, IOD, SGL, recx, epoch, and dkey hash state for either single-value or extent-value updates. `vts_dtx_commit_visibility()` and `vts_dtx_abort_visibility()` are the primary visibility harnesses.

## Control Flow

Tests `dtx_6`-`dtx_9` write with a prepared DTX, confirm data is invisible, commit it, confirm visible, then prepare a key/object punch and verify visibility changes only after commit. Tests `dtx_10`-`dtx_13` do the same for abort: an aborted update or punch must not affect the previously visible data.

`dtx_14` verifies double-commit is harmless and committed DTX cannot be aborted. `dtx_15` verifies double-abort/commit-after-abort does not reveal aborted data. `dtx_16` uses fault injection to simulate non-leader fetch behavior and checks `vos_dtx_mark_committable()` makes prepared data readable from the CoS cache. `dtx_17` iterates dkeys and sees only committed DTXs until the remaining transactions are committed. `dtx_18` commits ten DTXs, aggregates committed DTX metadata, checks committed stats drop to zero, and verifies data remains readable.

## State And Persistence Behavior

The tests write real VOS records under transactional metadata. Prepared DTXs must hide data and punches; commit and abort mutate DTX state and visibility. DTX aggregation removes committed DTX metadata while preserving data records. `sleep(3)` in `dtx_18` gives commit statistics enough time to age before aggregation.

## Dependencies And Integration Points

The file depends on DAOS DTX server internals, VOS types, `vts_io.h`, Murmur hashing, HLC timestamps, fail injection, VOS DTX APIs, object punch/update/fetch, and iterators. It exports `run_dtx_tests()` and helper functions declared by `vts_common.h`.

## Risks And Test Signals

Risks include DTX handle lifetime leaks, incorrect visibility for prepared records, punches becoming visible too early, iterator leakage of uncommitted dkeys, and aggregation removing needed data. Passing signals are memory equality/inequality around fetches, exact commit/abort return codes, expected iterator found sets, and `vos_dtx_check()` returning `-DER_NONEXIST` after aggregation.
