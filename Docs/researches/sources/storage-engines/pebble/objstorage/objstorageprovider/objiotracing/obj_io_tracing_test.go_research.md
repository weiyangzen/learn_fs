<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go

Purpose: integration test for object-I/O tracing under the `pebble_obj_io_tracing` build tag.

Important APIs and functions: `TestTracing` writes, flushes, compacts, closes, reads raw `IOTRACES-*` files back into `objiotracing.Event` values, and asserts important event fields.

Control flow: the test skips if tracing is disabled. It creates a MemFS DB, performs writes/flushes/compactions to generate read and write I/O, closes the DB to flush traces, collects and deletes trace files, counts matching events, then reopens and performs Gets to verify data-block read metadata.

State and persistence: trace files are persisted in MemFS as raw binary events. `collectEvents` reads whole files, checks their byte length is a multiple of event size, converts bytes to `Event` slices with `unsafe`, and removes files to isolate phases.

Dependencies and integration: integrates Pebble DB operations, object storage provider tracing wrappers, `vfs`, `blockkind`, and raw event schema layout.

Risks and gaps: assertions are mostly lower-bound existence checks rather than exact event sequences. It does not validate ordering or every context field. Unsafe conversion relies on event alignment and layout.

Test signals: confirms tracing captures reads and writes, file numbers, nonzero offsets, flush and compaction reasons, writes at L0 and L6, and L6 SSTable data-block reads after reopening.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_test.go -->
