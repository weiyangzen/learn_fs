# sources/storage-engines/wiredtiger/test/utility/disagg.c

## Purpose

`disagg.c` provides C test helpers for disaggregated-storage configuration and failure-time preservation of layered table components.

## Important APIs, Types, and Functions

Exports are `testutil_disagg_storage_configuration` and `testutil_disagg_preserve`. Internal `preserve_copy_uri` copies raw records from one URI to another, optionally under a read timestamp. `LAYERED_PREFIX` identifies layered table metadata entries.

## Control Flow

Configuration helper fills extension and connection config strings when disagg is enabled, optionally appending key-provider extension config; otherwise it emits empty config. Preserve helper opens source sessions plus a destination WiredTiger home under a subdirectory, copies metadata, iterates layered metadata URIs, and copies ingest, stable, and layered views into regular preserve tables before checkpointing and closing the destination.

## State and Persistence Behavior

It writes config strings into caller buffers and creates a separate preserved WiredTiger database containing copied metadata and table contents. Timestamped reads can snapshot data at a divergence point.

## Dependencies and Integration Points

Depends on `TEST_OPTS`, testutil environment config macros, WiredTiger raw cursors, timestamp transactions, layered URI naming conventions, and `testutil_format_item`.

## Risks and Edge Cases

Missing component files are logged and skipped, not fatal. Destination table names avoid `.wt_ingest` and `.wt_stable` substrings because WiredTiger treats those specially.

## Test Signals

Signals are correctly formed disagg extension/connection configs and preserved metadata/ingest/stable/layered tables in the destination home after failure handling.
