# sources/user-network-fs/rclone/fs/object/object.go

## Purpose
`object.go` defines lightweight object implementations used by tests and internal operations: immutable `StaticObjectInfo`, an in-memory `MemoryFs`, and mutable `MemoryObject`.

## Important APIs, types, and functions
Exports include `StaticObjectInfo`, `NewStaticObjectInfo`, `WithMetadata`, `WithMimeType`, `MemoryFs`, `MemoryObject`, `NewMemoryObject`, `SetFs`, `Content`, `Open`, `Update`, and interface methods for `fs.ObjectInfo`, `fs.Object`, `fs.Metadataer`, and `fs.MimeTyper`.

## Control flow
`NewStaticObjectInfo` stores caller-provided metadata and, if hashes are nil but an fs is supplied, creates empty hash entries for every supported hash type. `MemoryFs.Put` creates a `MemoryObject` and calls `Update`. `MemoryObject.Open` interprets `RangeOption` and `SeekOption`, clamps negative offsets, and returns an `io.NopCloser` over a slice. `Update` reuses the existing buffer when known size fits capacity, otherwise reads all content; it also updates modtime.

## State and persistence behavior
All object content, metadata, MIME type, and modtime live in memory. `MemoryFs` is a package-level value but has no backing store or directory tree. No data persists across process lifetime.

## Dependencies and integration points
The package depends on core `fs` interfaces, `hash.MultiHasher`, open options, and standard I/O. It is widely useful for unit tests, metadata mapper tests, and operations needing synthetic `ObjectInfo`.

## Risks and edge cases
`MemoryObject.Open` silently logs unsupported mandatory options rather than returning an error. Negative ranges and limits are simplified. `Update` with unknown size reads all input into memory. `MemoryFs` reports all hashes supported but has no object lookup store.

## Test signals
`object_test.go` covers static object properties/hash behavior, memory fs basics, Put, in-memory hashing, range/seek open behavior, modtime updates, buffer reuse/non-reuse, streaming unknown-size update, zero-length update, and unsupported remove.

Source-read signal: reviewed complete local file (349 lines). Types observed: `StaticObjectInfo`, `memoryFs`, `MemoryObject`. Functions/methods observed: `NewStaticObjectInfo`, `WithMetadata`, `WithMimeType`, `Fs`, `Remote`, `String`, `ModTime`, `Size`, `Storable`, `Hash`, `Metadata`, `MimeType`, `Name`, `Root`, `String`, `Precision`.
