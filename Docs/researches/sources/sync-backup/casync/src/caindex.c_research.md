# sources/sync-backup/casync/src/caindex.c

## Purpose
Implements `CaIndex`, the casync chunk index reader/writer. It writes and validates `.caidx`-style indexes containing an `INDEX` header followed by a `TABLE` of monotonically increasing chunk end offsets and chunk IDs, and supports both normal cooked operation and incremental raw streaming for uploads/downloads.

## Important APIs, Types, and Functions
Constructors select mode: `ca_index_new_write`, `ca_index_new_read`, `ca_index_new_incremental_write`, and `ca_index_new_incremental_read`. Setup includes fd/path/mode, feature flags, and chunk size bounds. Main operations are `ca_index_open`, `ca_index_write_chunk`, `ca_index_write_eof`, `ca_index_read_chunk`, incremental raw write/read/eof, size/count getters, and `ca_index_seek`.

## Control Flow
Opening lazily opens an fd. Writers use a temporary path when a final path is supplied, write the header once, append table items for each chunk, and finish with `CaFormatTableTail`; `ca_index_install` renames the temporary file after EOF. Readers validate the header, read table items sequentially, detect the tail marker, verify no trailing garbage, and reject non-monotonic or too-large chunk ranges. Incremental-read mode accepts raw bytes through `ca_index_incremental_write` while cooked reads return `-EAGAIN` until enough bytes are available. Incremental-write mode exposes newly written raw bytes via `ca_index_incremental_read`.

## State and Persistence Behavior
Persistent state is the index file: feature flags, chunk size min/avg/max, chunk end offsets, chunk IDs, and table tail marker/size. In-memory offsets (`start_offset`, `cooked_offset`, `raw_offset`, `item_position`, `previous_chunk_offset`) track raw/cooked progress. Blob size is cached from the final table item, and file size is cached for regular read mode.

## Dependencies and Integration Points
Depends on `caformat.h`, `caformat-util.h`, `cachunk.h`, `ReallocBuffer`, and utility I/O helpers. It connects chunking/storage code to archive data by mapping payload offsets to chunk IDs and skip amounts.

## Risks
Index correctness relies on offset monotonicity, tail validation, and matching chunk-size limits. The first chunk's returned size can be `UINT64_MAX` because there is no previous end offset in sequential reads, so callers must handle that convention. Temporary install is not complete until EOF and rename. Incremental modes are stateful and return `-EAGAIN` for legitimate partial data.

## Test Signals
Write/read round trips, zero-chunk index tails, malformed headers/tails/trailing bytes, non-monotonic offsets, chunk-size-limit rejection, temporary install behavior, incremental upload/download partial feeds, bisection seek at first/middle/last chunk boundaries, and overflow checks are important.
