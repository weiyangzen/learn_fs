# sources/storage-engines/wiredtiger/src/include/meta.h

## Purpose
Centralizes metadata filenames, metadata/system URI constants, metadata classification helpers, turtle-file locking, incremental backup state, and disaggregated metadata payload definitions.

## Important APIs, Types, And Functions
- File and URI constants include `WT_WIREDTIGER`, `WT_SINGLETHREAD`, `WT_BASECONFIG`, `WT_USERCONFIG`, `WT_METADATA_TURTLE`, `WT_METAFILE_URI`, history-store URIs, shared/disaggregated metadata URIs, and system timestamp URIs.
- URI classification macros include `WT_BTREE_PREFIX`, `WT_URI_IS_STABLE`, `WT_URI_IS_STABLE_CHECKPOINT`, `WT_URI_IS_INGEST`, `WT_IS_URI_HS`, `WT_HS_ID_TO_URI`, and `WT_IS_URI_METADATA`.
- Handle classification macros include `WT_IS_METADATA`, `WT_IS_DISAGG_META`, and `WT_IS_HS`.
- `WT_MIN_STARTUP_VERSION` defines the minimum compatible startup version.
- `WT_WITH_TURTLE_LOCK` serializes turtle-file operations.
- `struct __wt_blkincr` tracks block-incremental backup id, granularity, and flags.
- `WT_DISAGG_METADATA` holds checkpoint/key-provider strings, timestamps, schema epoch, file-id watermark, and metadata compatibility versions.

## Control Flow
Most definitions are constants or tests. `WT_HS_ID_TO_URI` switches known history-store IDs to URIs and asserts on unknown IDs. `WT_WITH_TURTLE_LOCK` asserts the session is not already marked as holding the turtle lock, then delegates to generic lock acquisition/release around the caller-provided operation.

## State And Persistence Behavior
The constants define persistent filenames, metadata keys, and stable URI identities used in database directories and metadata tables. `WT_DISAGG_METADATA` contains length-delimited metadata strings that are explicitly not null-terminated. `WT_BLKINCR` is connection runtime state for backup bookkeeping but refers to persistent checkpoint/file state.

## Dependencies And Integration Points
Depends on string macros from `misc.h`, data-handle flags, session lock flags, version types, timestamps, and schema locking macros. Integrated broadly with metadata open/upgrade, history store, backup, turtle file management, disaggregated storage, and system timestamp metadata.

## Risks
Changing constants can break existing database directories or metadata compatibility. Substring tests such as `WT_URI_IS_STABLE` are intentionally broad and must not be reused where strict suffix matching is required. `WT_DISAGG_METADATA` strings require length-aware handling. Turtle lock usage must match the global schema/metadata lock order to avoid deadlocks.

## Test Signals
Signals include upgrade/startup compatibility tests, metadata URI classification tests, history-store ID mapping assertions, turtle lock ordering tests, backup/incremental backup metadata tests, and disaggregated metadata parse/serialize tests with non-null-terminated strings.
