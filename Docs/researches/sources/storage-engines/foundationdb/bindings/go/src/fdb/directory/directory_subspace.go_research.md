<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go

Purpose: represents a concrete directory that can also be used as a FoundationDB subspace for application key/value content.

Important APIs: `DirectorySubspace` composes `subspace.Subspace` and `Directory`. `directorySubspace` stores the underlying subspace, directory layer, absolute path, and layer bytes. It forwards `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Move`, `Remove`, `Exists`, and `List` into the owning `directoryLayer` after combining the receiver path and relative path with `partitionSubpath`. `MoveTo` delegates to common `moveTo`; `GetLayer` and `GetPath` expose metadata; `String` prints path and raw prefix.

Control flow: this file is mostly an adapter. User calls on a directory subspace are translated into absolute directory-layer paths while all key packing/range behavior comes from the embedded `subspace.Subspace`.

State and persistence: no direct writes; persistence happens in `directoryLayer`. The stored `path` and `layer` are client-side descriptors of metadata read from FDB.

Dependencies and integration: integrates directory APIs with the lower-level `subspace` package and `fdb.Printable`. Returned by `directoryLayer.contentsOfNode` for non-partition directories.

Risks: path concatenation must remain consistent with partition semantics. Because the struct embeds `subspace.Subspace`, accidental copying is cheap but shares the same raw prefix. The returned `GetPath` slice is not cloned, so external mutation could surprise callers if they retain and modify it.

Test signals: expected coverage includes string rendering, relative directory operations, movement to absolute paths, and preservation of layer bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go -->
