# sources/object-store/daos/src/vos/tests/vts_ilog.c

## Purpose

`vts_ilog.c` tests VOS incarnation log behavior: update, punch replacement, abort, persist, aggregate, discard, validation, and version-cache changes. It uses a fake transaction-status layer so ilog code can be exercised without full DTX service state.

## Important APIs, Types, And Functions

`ilog_alloc_root()` and `ilog_free_root()` allocate/free an `ilog_df` root through `umem_tx_begin()`/`umem_tx_end()`. Fake transaction support is built from `struct fake_tx_entry`, global `fake_tx_list`, `current_status`, and `current_tx_id`. The callbacks in `ilog_callbacks` implement status lookup, same-transaction detection, log add, and log delete using an `lru_array`.

`struct entries` models the expected ilog sequence. `entries_init()` creates the LRU array and expected-entry buffer. `entries_set()` updates the expected sequence, and `entries_check()` runs `ilog_fetch()` and compares epoch and punch bits. `do_update()` wraps `ilog_update()` and encodes when an update should be appended to the expected model. `version_cache_fetch_helper()` checks `ilog_version_get()` increments only when expected.

## Control Flow

`ilog_test_update()` creates/open an ilog, inserts updates, upgrades same-epoch updates to punches, persists a transaction, verifies same-epoch conflict return codes, and appends many records with mixed statuses. `ilog_test_abort()` aborts existing and non-existing IDs, repeatedly inserts and aborts entries, and checks a destroyed/reallocated ilog cannot be opened. `ilog_test_persist()` persists entries out of order and validates visible log content.

`ilog_test_aggregate()` commits fake transactions, aggregates epoch ranges, and expects old entries to collapse to the correct surviving update or punch, eventually returning an empty-log signal. `ilog_test_discard()` runs similar aggregation with discard semantics, where ranges are removed instead of compacted. `ilog_is_valid_test()` directly constructs embedded and array ilog roots in a VMEM umem instance and verifies DTX LID/epoch matching behavior.

## State And Persistence Behavior

The tests allocate real umem-backed ilog roots from the VOS pool fixture. Fake transaction entries persist only in memory but are linked to ilog entry offsets and epochs. Persist, abort, aggregate, and destroy paths must delete fake tx entries so `fake_tx_list` is empty at the end. Version cache assertions detect missing or spurious ilog version bumps.

## Dependencies And Integration Points

The file depends on `vts_io.h`, VOS internals, `ilog_internal.h`, umem, LRU arrays, cmocka, and the common I/O fixture. It exports `run_ilog_tests()`, with `setup_ilog()` allocating `struct entries` in `io_test_args->custom`.

## Risks And Test Signals

Risks include leaked fake transaction entries, incorrect same-epoch conflict handling, aborted prepared entries staying visible, aggregation removing the wrong punch/update, and invalid ilog roots being accepted. Passing signals include exact fetched entry sequences, expected return codes (`-DER_ALREADY`, `-DER_TX_RESTART`, `-DER_NONEXIST`, empty-log return `1`), version changes only on mutation, and empty fake transaction lists after cleanup.
