# sources/storage-engines/wiredtiger/test/utility/tiered.c

## Purpose
`tiered.c` contains the runtime support needed by tests that optionally use WiredTiger tiered storage. It initializes tiered flush scheduling, sleeps until the next scheduled flush, updates scheduling after flush completion, and builds the tiered storage and extension configuration strings consumed by `testutil_wiredtiger_open`.

## Important APIs and functions
The exported functions are `testutil_tiered_begin`, `testutil_tiered_end`, `testutil_tiered_sleep`, `testutil_tiered_flush_complete`, and `testutil_tiered_storage_configuration`. The implementation reads and mutates `TEST_OPTS` fields such as `tiered_storage`, `tiered_begun`, `tiered_flush_interval_us`, `tiered_flush_next_us`, `absolute_bucket_dir`, `make_bucket_dir`, `build_dir`, artificial delay/error settings, `local_retention`, `home`, and `tiered_storage_source`.

## Control flow and behavior
`testutil_tiered_begin` asserts a connection exists, optionally opens a temporary session to schedule the first flush, and marks tiered state begun. `testutil_tiered_sleep` calculates an absolute wake time, shortens it to the next tiered flush if appropriate, sleeps in at-most-one-second chunks while `opts->running`, and tells the caller when to run `flush_tier`. `testutil_tiered_flush_complete` schedules the next flush. `testutil_tiered_storage_configuration` only supports `dir_store`, builds the extension string, computes bucket paths, optionally creates the bucket directory, and emits empty config when tiered storage is disabled.

## State, dependencies, and integration
This file depends on `test_util.h`, WiredTiger time/sleep helpers through `testutil_time_us`, the `DIR_STORE` macros, and the extension config macros. It integrates with command-line parsing from `parse_opts.c`, connection opening in `misc.c`, and test loops that periodically call `flush_tier`.

## Risks and test signals
Risks include path-buffer limits, `mkdir` failure if the bucket exists unexpectedly, `do_flush_tier` being dereferenced even though the function only conditionally checks it earlier, and strict support for `dir_store` only. Signals include tiered tests opening the storage source extension, bucket directory creation, periodic flush scheduling, and no repeated flush attempts while a previous flush is still considered incomplete.
