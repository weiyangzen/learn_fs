# sources/object-store/openstack-swift/swift/obj/mem_diskfile.py

## Purpose
`mem_diskfile.py` is a sample in-memory implementation of the Swift diskfile interface. It duck-types the core `DiskFile`, `DiskFileWriter`, and `DiskFileReader` behavior needed by the object server, but stores object bytes and metadata in a Python dictionary instead of a POSIX filesystem. It is useful for lightweight testing, demonstration, and the companion in-memory object server.

## Important APIs, Types, And Functions
`InMemoryFileSystem` owns the process-local storage dictionary. `get_object()` returns a `(BytesIO, metadata)` pair or `(None, None)`. `put_object()` stores an object. `del_object()` deletes an object. `get_diskfile()` creates a `DiskFile`. `pickle_async_update()` is a no-op because this backend does not persist async container updates.

`DiskFileWriter` buffers a PUT into a new `io.BytesIO`, updates upload size and md5 in `write()`, reports `(upload_size, etag)` from `chunks_finished()`, stores metadata plus `name` into the in-memory filesystem in `put()`, and has a no-op `commit()`.

`DiskFileReader` wraps a `BytesIO` and implements full-object iteration, single-range iteration, multi-range iteration via `multi_range_iterator`, close-time length and etag validation, and quarantine recording through `was_quarantined`. It does not physically move data on quarantine.

`DiskFile` represents one object name. `open()` fetches the in-memory object, verifies metadata, expiration, content length, and path/name match, and returns itself. `get_metadata()`, `get_datafile_metadata()`, and `get_metafile_metadata()` return the same metadata dictionary. `reader()` transfers the buffer to a `DiskFileReader`. `create()` yields a writer. `write_metadata()` applies fast-POST-like metadata updates while preserving immutable datafile metadata and object sysmeta. `delete()` removes an object if the provided timestamp is newer than stored metadata. Timestamp and content-type properties mirror the disk backend.

## Control Flow
PUT-like flows call `DiskFile.create()`, receive an opened `DiskFileWriter`, write chunks, then call `put(metadata)` to store the completed `BytesIO` and metadata under the full `/account/container/object` name. If `put()` is not called before the context closes, the buffered data is discarded.

GET/HEAD-like flows call `open()`. Missing objects raise `DiskFileDeleted`. Existing objects are checked for required `name` and `Content-Length` metadata, optional integer `X-Delete-At`, name/path collision, expiration, and actual buffer length. `reader()` then returns an iterator that reads the buffer, optionally validates md5 when read from offset zero through EOF, and clears its file pointer on close.

POST-like flows call `write_metadata()`, which fetches existing data and metadata, preserves reserved datafile metadata (`content-length`, `deleted`, `etag`), datafile system metadata, and object sysmeta, sets the canonical `name`, and replaces metadata in the store. DELETE removes the entry only when the existing `X-Timestamp` is older than the delete timestamp; it does not write tombstones.

## State, Persistence, And Dependencies
All state is process-local and volatile in `InMemoryFileSystem._filesystem`. Values are `(BytesIO, metadata)` pairs keyed by full object name. There are no directories, xattrs, hashes, tombstones, async updates, replication locks, recon outputs, or durable EC markers. Expiration is enforced on open by checking `X-Delete-At` against current time.

Dependencies are intentionally narrow: `io.BytesIO`, `time`, `contextmanager`, Swift timestamp and md5 helpers, diskfile metadata constant sets, `is_sys_meta()`, Swift diskfile exceptions, `Timeout`, and `multi_range_iterator`.

## Integration Points
`mem_server.py` uses `InMemoryFileSystem` as the storage backend for an in-memory object server. The class and method names match enough of `swift.obj.diskfile` for object-server code paths to exercise PUT, GET, HEAD, POST, and DELETE behavior without a real device tree.

The backend borrows metadata rules from `diskfile.py` by importing `DATAFILE_SYSTEM_META` and `RESERVED_DATAFILE_META`, so fast-POST immutability rules stay aligned with the reference backend.

## Risks
This implementation is not durable, not thread-safe beyond ordinary Python object behavior, and not semantically complete compared to `diskfile.py`. Deletes remove entries rather than writing tombstones, quarantine deletes the in-memory entry rather than preserving evidence, async updates are dropped, and replication support is absent. `DiskFileReader.app_iter_range()` yields an overlong final chunk using `chunk[:length]` after `length` is negative, matching the file's current logic but requiring careful tests for range truncation.

Because `BytesIO` objects are stored directly and reused, callers that retain references could observe shared mutable state. Metadata dictionaries are also stored by reference unless callers copy them. This is acceptable for a sample/test backend but risky for production-like use.

## Test Signals
Tests should cover create/write/put/read round trips, metadata validation failures, expiration handling, path collision, length mismatch quarantine, etag mismatch quarantine, metadata update preserving immutable keys and sysmeta, timestamp-based delete behavior, missing-object exceptions, range and multi-range iteration, and no-op async update behavior. Tests should also assert that state disappears across new `InMemoryFileSystem` instances because persistence is intentionally absent.
