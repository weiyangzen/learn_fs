<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh

## Purpose

`XrdPfcDirStateSnapshot.hh` declares flattened JSON-exportable directory state structures for XrdPfc resource monitor snapshots.

## Important APIs, Types, And Functions

- `DirStateElement` extends `DirStateBase` with snapshot `DirStats`, combined `DirUsage`, parent index, and daughter index range.
- `DataFsSnapshot` extends `DataFsStateBase` with `m_dir_states` and `m_sshot_stats_reset_time`.
- `write_json_file()` persists a snapshot through `XrdOss`.
- `dump()` prints the snapshot as JSON.

## Control Flow

Resource monitor code converts live `DirState` trees into `DataFsSnapshot` vectors. This header keeps the flattened representation independent from live child maps, while the implementation handles serialization and cache-file writing.

## State And Persistence

The structures hold snapshot data in memory. `write_json_file()` persists it as a data file plus `.cinfo`.

## Dependencies And Integration Points

It includes `XrdPfcDirState.hh` and `vector`, and forward-declares `XrdOss`. It bridges resource monitor state to on-disk JSON reporting.

## Risks And Edge Cases

- Parent/daughter indices must be built consistently by external conversion code.
- Snapshot stats use `m_sshot_stats`, so callers must reset snapshot stats at the right time to avoid duplicate reporting.
- The representation does not validate tree consistency.

## Test Signals

Tests should validate construction from `DirState`, vector parent/daughter consistency, serialized field coverage through the implementation, and reset timestamp propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh -->
