# sources/storage-engines/foundationdb/fdbclient/BulkLoading.cpp

## Purpose

`BulkLoading.cpp` provides small but central utility functions for FoundationDB bulk dump/load metadata. It validates whether a data movement ID represents a logical or physical bulk-load move, converts manifest metadata into native `Key` values, normalizes blobstore/local paths, formats bulk-load enum values for diagnostics, and builds simple `BulkLoadTaskState` / `BulkLoadJobState` instances for manual or test submission.

## Important APIs, Types, And Functions

The public helpers are free functions declared by `fdbclient/BulkLoading.h`. `getConductBulkLoadFromDataMoveId()` decodes the encoded data-move UID via `decodeDataMoveId()` and asserts the invariants required for bulk-load moves: non-empty range, valid non-anonymous shard ID, and assigned state. `dataMoveIdIsValidForBulkLoad()` is the simpler validity predicate used by that assertion. `stringRemovePrefix()` is a strict manifest parser helper that throws `bulkload_manifest_decode_error` if the expected prefix is absent.

`getKeyFromHexString()` converts a space-delimited hex byte string such as `01 02 03` into an FDB `Key`, asserting the exact two-hex-digits-plus-space layout. Filename helpers standardize the job manifest name, byte-sample suffix, and empty manifest name. `convertBulkLoadJobPhaseToString()` and `convertBulkLoadTransportMethodToString()` translate enums into stable trace/user strings and emit error trace events on unexpected values.

The URL helpers use `BLOBSTORE_URL_PATTERN` plus Boost.URL. `getPath()` strips blobstore credentials before parsing and returns the object path without a leading slash. `appendToPath()` preserves the blobstore scheme and optional credentials while replacing the parsed path with a `joinPath()` result. `getBackupDataPath()` rewrites the path under `data/<original>/<suffix>` for backup-container data layout. `getBulkLoadJobRoot()` appends the job UID string to a root URL/path.

## Control Flow

Most functions are synchronous validators/formatters. Blobstore path functions first check whether the input matches `blobstore://...`; local paths fall back to `joinPath()`, while blobstore URLs are parsed after credentials are removed because Boost.URL cannot digest the credential format used here. Parse failures are traced and rethrown as `std::invalid_argument`.

`createBulkLoadTask()` constructs a `BulkLoadManifest`, places it into a single-entry `BulkLoadManifestSet`, and wraps it in `BulkLoadTaskState`. `createBulkLoadJob()` directly constructs a `BulkLoadJobState`.

## State And Persistence

This file does not persist state itself. It encodes naming and path conventions that downstream bulk dump/load actors use when writing manifests and data to local files or blobstore. The task/job construction helpers create in-memory state objects that other bulk-loading code persists through system keys or task metadata.

## Dependencies And Integration Points

Dependencies include `fdbclient/BulkLoading.h`, `fdbclient/SystemData.h`, Boost.URL, Flow tracing/assertion utilities, and system-data functions such as `decodeDataMoveId()`. The helpers integrate with data movement, backup-container path layout, bulk dump/load manifest parsing, and tests or manual task submission flows.

## Risks And Test Signals

The blobstore regex only supports the current `blobstore://` form and has a TODO for `file://`; any credential or URL grammar change can break path preservation. `getKeyFromHexString()` relies on assertions for layout validation, so malformed release-build input may surface as `std::stoul` exceptions or unchecked behavior. Important tests include `bulkload_test` from this directory's CMake file and unit or simulation coverage around credentialed blobstore URLs, local paths, empty keys, and invalid manifest prefixes.
