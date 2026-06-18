# sources/storage-engines/sqlite/ext/misc/fossildelta.c

## Purpose

`fossildelta.c` implements Fossil delta creation, application, output-size inspection, and delta parsing for SQL. It is provided mainly for developers inspecting RBU files that contain Fossil-format deltas.

## Important APIs, types, and functions

`sqlite3_fossildelta_init()` registers scalar functions `delta_create(X,Y)`, `delta_apply(X,D)`, `delta_output_size(D)`, and virtual table `delta_parse`. The delta engine uses `hash` for a 16-byte rolling checksum window (`NHASH`), `putInt()` and `deltaGetInt()` for Fossil base-64 integers, `checksum()` for the 32-bit big-endian output checksum, `delta_create()`, `delta_output_size()`, and `delta_apply()`.

The parser virtual table uses `deltaparsevtab_cursor`, which stores a copy of the delta blob, cursor offsets, current operator, and operator arguments. It exposes columns `op`, `a1`, `a2`, and hidden `delta`.

## Control flow

`delta_create()` writes the target size line, builds a hash table over 16-byte source landmarks, scans the target with a rolling hash, chooses copy commands when they are smaller than literal text, emits insert commands for unmatched bytes, and finishes with a checksum record. Copy records have `N@O,`, inserts have `N:<bytes>`, and checksum has `N;`.

`delta_apply()` reads the expected output size, then processes copy, insert, and checksum operators while enforcing output-size and source-bound limits. It returns -1 for malformed deltas. Checksum verification is compiled only when `FOSSIL_ENABLE_DELTA_CKSUM_TEST` is defined, but size and bounds checks always run. SQL wrappers allocate output buffers based on `delta_output_size()` and report `"corrupt fossil delta"` on parse/apply mismatch.

`delta_parse` requires an equality constraint on hidden `delta`. `deltaparsevtabFilter()` copies the delta blob and emits the initial `SIZE` row. `deltaparsevtabNext()` advances through operators and emits `COPY`, `INSERT`, `CHECKSUM`, `ERROR`, or `EOF`. Insert payloads are returned as blobs; malformed insert lengths return a zeroblob in `a2`.

## State and persistence

The scalar functions are stateless and operate on input blobs. The parser virtual table stores only cursor-local copies of delta blobs. No database writes occur.

## Dependencies and integration points

It depends on SQLite loadable extension APIs, virtual table APIs, SQLite integer typedefs, and the Fossil delta format also used by SQLite RBU artifacts. Functions are registered as UTF-8 innocuous.

## Risks

Delta data is binary and can contain embedded NULs, so all paths must use explicit byte lengths. `delta_create()` allocates hash arrays proportional to source length and a caller-provided output buffer sized by the SQL wrapper as `target+70`. `checksum()` assumes four-byte alignment in an assert and has endian-specific fast paths. `delta_apply()` protects against output overflow, source overread, missing terminators, and oversized inserts, but checksum validation is optional at compile time. The parser is diagnostic and may expose partial/error rows rather than rejecting all malformed input at filter time.

## Test signals

Tests should round-trip small and large text and binary blobs, source shorter than `NHASH`, insert-only deltas, copy-heavy deltas, embedded NUL data, malformed size headers, bad copy terminators, source-overrun copy commands, output-size mismatch, truncated inserts, checksum rows, `delta_output_size()` errors, `delta_parse` row sequences, hidden-delta planning constraints, and optional checksum-failure behavior when compiled with checksum testing.
