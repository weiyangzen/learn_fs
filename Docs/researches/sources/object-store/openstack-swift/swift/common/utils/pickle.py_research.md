# sources/object-store/openstack-swift/swift/common/utils/pickle.py

## Purpose
This small module provides durable pickle writes and restricted pickle reads for the limited Swift data structures that still use pickle serialization. It narrows the default Python pickle attack surface by whitelisting the globals required by Swift's legacy serialized data.

## Important APIs, Types, and Functions
- `write_pickle(obj, dest, tmp=None, pickle_protocol=0)` serializes an object to a temporary file, flushes and `fsync()`s it, then atomically renames it into place with Swift's `renamer()`.
- `_ALLOWED_GLOBALS` is the whitelist for unpickling globals: `_codecs.encode`, `copyreg._reconstructor`, `HeaderKeyDict`, `dict`, and `bytes`, with Python 2 compatibility aliases.
- `RestrictedUnpickler.find_class()` permits only whitelisted `(module, name)` pairs and raises `pickle.UnpicklingError` for everything else.
- `unpickle(source, encoding='ASCII')` mirrors `pickle.loads()` for bytes or file-like input while using `RestrictedUnpickler`.

## Control Flow and Behavior
`write_pickle()` ensures the temporary directory exists, creates an exclusive temp file with suffix `.tmp`, writes pickle bytes, flushes Python buffers, fsyncs the fd, and performs an atomic rename. `unpickle()` wraps raw bytes in `io.BytesIO`; other sources are passed directly to `pickle.Unpickler`.

## State and Persistence
The module persists serialized state on disk via pickle files. Durability is handled for the file content itself before rename; parent-directory fsync is not done here. The allowed globals table is static module state.

## Dependencies and Integration Points
It depends on `swift.common.header_key_dict.HeaderKeyDict`, `mkdirs()`, and `renamer()`. It integrates with Swift code that needs old pickle formats while enforcing a known-safe set of classes.

## Risks and Edge Cases
- Pickle remains a sensitive format; the whitelist must be kept tight and expanded only after compatibility and security review.
- `pickle_protocol=0` defaults to ASCII protocol for legacy compatibility, which may be slower/larger than modern protocols.
- Atomic rename does not by itself guarantee parent-directory durability after a crash on all filesystems.
- File-like sources passed to `unpickle()` must be positioned correctly by the caller.

## Test Signals
Tests should assert atomic temp cleanup behavior on success/failure, fsync invocation, round-trips for allowed `HeaderKeyDict`, rejection of arbitrary globals, bytes and file-like unpickle inputs, and compatibility with Python 2 module-name aliases embedded in older pickles.
