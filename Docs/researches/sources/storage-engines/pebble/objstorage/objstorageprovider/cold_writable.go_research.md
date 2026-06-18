<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go

Purpose: implements a writable wrapper that writes the full object to cold storage while duplicating the metadata suffix to a hot local metadata file after `StartMetadataPortion`.

Important APIs and types: `newColdWritable` constructs `coldWritable`, which implements `objstorage.Writable`. Key methods are `Write`, `StartMetadataPortion`, `flushMeta`, `Finish`, `Abort`, `deleteMetaFile`, and `metaPath`.

Control flow: before metadata starts, `Write` forwards to cold storage and increments `startOffset`. After metadata starts, `Write` copies bytes into an internal 4KiB buffer and flushes to the hot metadata file as needed, then writes to cold storage. `StartMetadataPortion` creates the hot metadata file and forwards the signal to the cold writer. `Finish` flushes/syncs/closes metadata first, finishes cold storage, then registers the metadata sidecar with the provider. `Abort` closes/removes the metadata file and aborts cold storage.

State and persistence: tracks metadata start offset, hot file handle, buffer, and sticky error. Durability is carefully ordered so a crash leaves either no metadata file or one discoverable/cleanable with the cold object.

Dependencies and integration: used by provider cold-tier creation. Depends on provider metadata path/registration methods, `vfs.File`, `objstorage.Writable`, and `firstError`.

Risks and edge cases: local `vfs.File.Write` may mangle input buffers, so the code copies before writing. Once `w.err` is set, subsequent calls return it. `StartMetadataPortion` is idempotent but repeated calls do not signal cold writer again.

Test signals: no direct listed tests; correctness should be covered by cold-tier creation/reopen/delete integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_writable.go -->
