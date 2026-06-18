<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go

Purpose: implements binary object-I/O tracing when built with `pebble_obj_io_tracing`, wrapping object readers, read handles, and writers to emit `Event` records to `IOTRACES-*` files.

Important APIs and types: `Enabled` is true. `Tracer` owns the filesystem, output directory, atomic handle IDs, worker channels, and worker goroutine. Wrappers `writable`, `readable`, and `readHandle` implement the object I/O interfaces. Context helpers store `ctxInfo` for reason, block kind, and level. `eventGenerator` buffers events locally before sending `eventBuf`s to the worker.

Control flow: `Open` starts the worker. Wrapper methods record events before delegating to underlying I/O; `Finish`, `Abort`, `Close`, and read-handle `Close` flush local buffers. Context metadata is merged with wrapper base metadata. The worker writes raw in-memory `Event` bytes through a buffered writer, rotates files after about 256MiB of events, and syncs/closes on shutdown.

State and persistence: persistent output is binary `IOTRACES-*` files in the provider directory. In-memory state includes per-wrapper event buffers, channel buffers, current trace file, and random/atomic handle IDs.

Dependencies and integration: used by `objstorageprovider.provider` when tracing is enabled. Depends on `unsafe` serialization, `vfs.NewSyncingFile`, context propagation from higher-level Pebble read/write paths, and `blockkind` metadata.

Risks and edge cases: worker errors panic. `readable.Close` flushes without locking around `mu.g`, so it assumes no concurrent reads during close. Channel send in `flush` can block under extreme event volume. Binary format assumes `Event` layout stability.

Test signals: tracing build-tag test checks reads, writes, flush/compaction reasons, L0/L6 levels, offsets, file numbers, and data-block reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_on.go -->
