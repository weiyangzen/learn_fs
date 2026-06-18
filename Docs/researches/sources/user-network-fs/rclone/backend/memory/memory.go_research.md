# sources/user-network-fs/rclone/backend/memory/memory.go

## Purpose
`memory.go` implements an in-memory, bucket-based rclone backend. It is primarily useful for tests and performance experiments, with an optional discard mode that records object metadata and MD5 while dropping data so reads fail. The backend supports buckets, empty directories as buckets, listing, recursive listing, copy, streaming put, MIME metadata, nanosecond modtime precision, and MD5 hashes.

## Important APIs, Types, And Functions
`Options` has the `Discard` flag. `Fs` stores name, root, parsed bucket and directory, options, and features. Global `buckets` is a process-wide `bucketsInfo` containing a map of bucket names to `bucketInfo`. `bucketInfo` stores object path keys to `objectData`. `Object` holds its `Fs`, remote path, and pointer to `objectData`.

Important functions include `NewFs`, `parsePath`, `Fs.split`, `setRoot`, `NewObject`, `list`, `listDir`, `listBuckets`, `List`, `ListP`, `ListR`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, `Copy`, `Hashes`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Hash`, `SetModTime`, and `MimeType`.

## Control Flow
`NewFs` parses options, trims root, splits bucket/directory, fills features, and detects whether the configured root points to an existing object. If root is an object path, it returns an Fs rooted at the parent and `fs.ErrorIsFile`.

Object writes create a temporary `Object` and call `Update`. In normal mode, `Update` reads the whole input into memory, sets size, modtime, MIME type, and leaves hash lazy. In discard mode, it streams through MD5, records only size/hash/modtime/MIME, and leaves `data` nil. `Open` honors seek and range options by slicing the stored byte slice unless discard mode is enabled, in which case it returns `errWriteOnly`.

Listing delegates through `list.WithListP`. Bucket-root listing returns bucket directories. Bucket listing scans the map under the bucket read lock, emits direct child dirs when not recursing, and emits objects otherwise. `ListR` intentionally collects entries before calling the list helper to avoid deadlock between listing and callbacks that may remove objects. Copy shallow-copies `objectData` metadata and data slice pointer from another memory object.

## State And Persistence Behavior
All objects are process-global in `buckets`; they persist across Fs instances in the same process and disappear when the process exits. `bucketsInfo.mu` protects the bucket map, and each bucket has its own RW mutex for object maps. `objectData` fields themselves are not individually synchronized after lookup, so concurrent mutation of a live object's modtime/hash/data through existing object pointers can race if callers share objects unsafely.

Bucket removal deletes only empty buckets. Directory objects are virtual, inferred from object key prefixes. The backend does not persist explicit non-bucket empty directories.

## Dependencies And Integration Points
The backend integrates with rclone's bucket path helper, list helper, configstruct, hash, MIME detection, optional `Copier`, `PutStreamer`, `ListRer`, `ListPer`, and `MimeTyper` interfaces. It is often used by rclone tests via the `:memory:` connection string.

## Risks And Edge Cases
Global process state can leak between tests if roots collide. Copy duplicates the `objectData` struct but not the underlying data slice, which is acceptable for immutable updates because `Update` replaces the whole pointer but can surprise code that mutates slices directly. The listing scan uses map iteration order, so output order is intentionally nondeterministic. `Mkdir` with an empty bucket name can create an empty-name bucket if invoked at root in unusual paths. Discard mode advertises written objects but all reads fail.

## Test Signals
Integration tests run in quick mode against `:memory:`. The internal deadlock test specifically validates that fallback purge does not deadlock when recursive listing and removals interact. Useful additional tests include global-state isolation, discard mode reads/hashes, range reads, root-as-file detection, bucket deletion errors, and concurrent update/list behavior under the race detector.
