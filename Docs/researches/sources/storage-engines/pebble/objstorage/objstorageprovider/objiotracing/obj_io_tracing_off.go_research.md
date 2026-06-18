<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go

Purpose: provides the no-op implementation of object-I/O tracing for normal builds without the `pebble_obj_io_tracing` build tag.

Important APIs and types: `Enabled` is false. `Tracer` is an empty struct. `Open` returns nil; `Close` is no-op; `WrapReadable` and `WrapWritable` return their inputs; `WithReason`, `WithBlockKind`, and `WithLevel` return the original context unchanged.

Control flow: all functions are pass-throughs to remove tracing overhead and side effects.

State and persistence: none. No trace files are created.

Dependencies and integration: selected by build constraint `!pebble_obj_io_tracing`. Provider code checks `objiotracing.Enabled` before opening/using a tracer, allowing tracing calls to compile away in regular builds.

Risks and edge cases: callers must guard nil tracer use through `Enabled`, as `Open` returns nil. Context metadata is intentionally discarded, so code must not rely on it outside tracing.

Test signals: `obj_io_tracing_test.go` skips when `Enabled` is false.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/objiotracing/obj_io_tracing_off.go -->
