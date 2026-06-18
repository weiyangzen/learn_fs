# sources/sync-backup/casync/src/caindex.h

## Purpose
Declares the opaque chunk-index API used by casync to create, stream, read, seek, and query chunk indexes.

## Important APIs, Types, and Functions
`CaIndex` is opaque. Constructors encode allowed operation modes. Setters configure fd/path, creation mode, feature flags, and chunk size bounds. The API supports opening/installing, writing chunk entries and EOF, reading cooked chunks, raw incremental write/read, position management, size/count getters, and blob-offset seeking.

## Control Flow
Typical writers configure chunk sizes/features then write chunks and EOF before install. Readers open and call `ca_index_read_chunk` until EOF or use `ca_index_seek` to position at the chunk containing a blob offset.

## State and Persistence Behavior
The header exposes index persistence through getters for index size, blob size, total chunks, available chunks, and chunk sizing. It intentionally hides internal fd/path/temp-file state.

## Dependencies and Integration Points
Includes `cachunkid.h` and `realloc-buffer.h`. Integrated with chunk store upload/download paths and archive payload readers.

## Risks
Mode-specific APIs return errors when used on the wrong constructor. Callers must set chunk sizes before writing and handle `-EAGAIN` in incremental modes.

## Test Signals
Mode matrix tests, wrong-mode error coverage, seek behavior, and incremental buffer API tests cover the public contract.
