# sources/sync-backup/borg/src/borg/helpers/msgpack.py

## Purpose
Wraps `msgpack` so Borg consistently uses binary/string settings, surrogateescape handling, bounded unpackers for untrusted data, and Borg-specific exception types.

## Important APIs, Types, And Functions
Constants `USE_BIN_TYPE=True`, `RAW=False`, `UNICODE_ERRORS="surrogateescape"`. Exceptions `PackException` and `UnpackException`. Wrappers `Packer`, `packb`, `pack`, `Unpacker`, `unpackb`, `unpack`. Utility exports include `is_slow_msgpack`, `is_supported_msgpack`, `get_limited_unpacker`, `int_to_timestamp`, `timestamp_to_int`, plus re-exported `ExtType`, `Timestamp`, and `OutOfData`.

## Control Flow
Pack wrappers assert Borg's unicode-error policy and translate any packing exception. Unpack wrappers preserve `OutOfData` for streaming callers but wrap other exceptions. `get_limited_unpacker` selects use-list and max-buffer policies by data kind: remote client/server get maximum buffers for large store operations, while manifest/archive/key get `StableDict` hooks and list behavior.

## State And Persistence
No persistent state. `is_supported_msgpack` reads `BORG_MSGPACK_VERSION_CHECK` each call. `Unpacker` instances hold stream buffers internally.

## Dependencies And Integration Points
Used by archive metadata, item serialization, key files, repository RPC, FUSE metadata, and JSON dump preparation. It depends on Borg constants and `StableDict` to preserve deterministic map ordering for selected unpacking paths.

## Risks And Edge Cases
Changing raw/bin defaults can break repository compatibility. `get_limited_unpacker("server"|"client")` intentionally disables max buffer limits for specific large operations, so callers must use the correct kind. Environment override can bypass version checks. Wrapping exceptions may hide original exception types unless callers inspect `args`.

## Test Signals
Existing msgpack tests should cover str/bytes round-trips with surrogateescape, streaming `OutOfData`, wrapped exceptions, supported-version environment override, limited unpacker settings, timestamp conversion, and legacy data compatibility.
