# sources/storage-engines/pebble/objstorage/objstorageprovider/shared_writable.go

Purpose: This file adapts a remote `io.WriteCloser` into Pebble's `objstorage.Writable` interface and performs shared-object ref-marker creation on successful finish.

Important APIs and types: `NewRemoteWritable` is a test/tool constructor that wraps an arbitrary `io.WriteCloser`. `sharedWritable` stores an optional provider, object metadata, and the underlying remote storage writer. It implements `Write`, `StartMetadataPortion`, `Finish`, and `Abort`.

Control flow: `Write` forwards bytes to the remote writer and returns its error. `StartMetadataPortion` is a no-op because remote shared objects do not split metadata in this wrapper. `Finish` closes the remote writer, nils it, and if associated with a provider creates the ref marker through `sharedCreateRef`. If close or marker creation fails, it calls `Abort`. `Abort` closes any live writer and removes provider metadata for the file number, but a TODO notes it does not delete the remote object if creation already occurred.

State and persistence: The remote object is finalized by closing the underlying writer; a ref marker is separately persisted for ref-tracked cleanup. Provider metadata removal during abort prevents the object from remaining known locally, but remote garbage may remain if abort follows partial upload.

Dependencies and integration: `remote.go` returns `sharedWritable` from `sharedCreate`. Provider metadata is added before/around creation by provider logic, and `sharedCreateRef` enforces creator ID and cleanup semantics.

Risks and test signals: The biggest risk is leaked remote objects on abort or ref-marker creation failure. Data-driven provider tests exercise successful shared create/remove and ref tracking, but the TODO indicates incomplete cleanup for failed writes.
