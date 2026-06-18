<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc

## Purpose

`XrdPfcDirStateSnapshot.cc` serializes flattened directory-state snapshots to JSON and writes them into the cache namespace as complete cache-managed files.

## Important APIs, Types, And Functions

- `PFC_DEFINE_TYPE_NON_INTRUSIVE` extends nlohmann JSON macros for both `json` and `ordered_json`.
- JSON serializers are defined for `DirStats`, `DirUsage`, `DirStateElement`, and `DataFsSnapshot`.
- `DataFsSnapshot::write_json_file()` writes snapshot JSON data and a synced `.cinfo` metadata file through `XrdOss`.
- `DataFsSnapshot::dump()` prints the ordered JSON representation to stdout.

## Control Flow

`write_json_file()` creates the target file in the configured data space, opens it, optionally wraps the snapshot under a `dirstate_snapshot` preamble, serializes ordered JSON, truncates and writes the data, then creates and writes the `.cinfo` file with all bits marked synced. `dump()` performs only in-memory serialization and stdout output.

## State And Persistence

The function persistently writes a JSON snapshot file and a corresponding `.cinfo` metadata file in the cache namespace. It uses configuration-derived user and space values and fixed advisory sizes/modes.

## Dependencies And Integration Points

It depends on `XrdPfcDirStateSnapshot.hh`, `XrdPfcPathParseTools`, `XrdPfc.hh`, `XrdPfcTrace`, `XrdOucJson`, `XrdOucEnv`, `XrdOss`, and `XrdPfcInfo`. It is used by resource monitor directory-stat reporting.

## Risks And Edge Cases

- Error handling is logging-only; callers do not receive success/failure.
- There are suspicious cleanup calls: after a failed `.cinfo` create/open, code references `myFile` after it has already been closed/deleted in the data-file phase.
- Writes do not check return length from `myFile->Write()`.
- JSON serialization can throw, and this function does not catch exceptions.
- The output mode is `0644`, making snapshots world-readable depending on OSS semantics.

## Test Signals

Tests should cover JSON field names/order, preamble on/off, OSS create/open/write failures for data and `.cinfo`, write-length failures, `.cinfo` completeness via `Info`, dump output, and exception behavior for serialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc -->
