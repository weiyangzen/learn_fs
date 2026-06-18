<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go

Purpose: defines the object-I/O tracing event schema shared by tracing-enabled and tracing-disabled builds.

Important APIs and types: `OpType` enumerates read, write, cache-hit, and setup-for-compaction operations. `Reason` captures high-level context such as flush, compaction, and ingestion. `Event` is the on-disk binary event format, including timestamp, op, reason, block kind, LSM level plus one, file number, read-handle ID, offset, and size.

Control flow: none; this file is schema declarations.

State and persistence: `Event` is explicitly the persisted trace record shape. Padding is hardcoded so struct layout is architecture-stable for trace files.

Dependencies and integration: used by `obj_io_tracing_on.go`, `obj_io_tracing_off.go`, trace-processing tools, and tracing tests. Depends on `base.DiskFileNum` and `blockkind.Kind`.

Risks and edge cases: binary trace compatibility depends on field layout and `unsafe` serialization in the on-build implementation. Adding fields or changing types requires trace reader coordination.

Test signals: `obj_io_tracing_test.go` reads raw trace files back into `Event` slices using `unsafe.Sizeof(Event{})`, validating the schema under the tracing build tag.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing.go -->
