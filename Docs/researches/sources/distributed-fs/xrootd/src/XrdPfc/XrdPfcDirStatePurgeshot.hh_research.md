<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh

## Purpose

`XrdPfcDirStatePurgeshot.hh` declares the flattened directory-usage view used by purge logic to make path-based usage queries without traversing the live `DirState` tree.

## Important APIs, Types, And Functions

- `DirPurgeElement` extends `DirStateBase` with combined `DirUsage`, parent index, and daughter index range.
- `DataFsPurgeshot` extends `DataFsStateBase` with purge target bytes, estimated write-queue writes, purge mode flags, and `m_dir_vec`.
- `find_dir_entry_from_tok()`, `find_dir_entry_for_dir_path()`, and `find_dir_usage_for_dir_path()` locate directory usage by path.

## Control Flow

The vector form represents a tree with contiguous daughter ranges. Path lookup tokenizes an absolute directory path, starts at root index 0, scans the current node's daughter range for each component, and returns either the matching entry or `-1`.

## State And Persistence

The structures are in-memory snapshots. They do not own live tree pointers and do not perform persistence. They carry purge intent fields such as bytes to remove and age/space mode flags.

## Dependencies And Integration Points

It depends on `XrdPfcDirStateBase.hh` and `XrdPfcPathParseTools.hh`. Resource monitor or purge code constructs it from live state; purge policy code can query it by directory.

## Risks And Edge Cases

- Lookup assumes `m_dir_vec[0]` exists and daughter ranges are valid.
- Daughter search is linear within each directory.
- `last_existing_entry` is only set on a failed component, not updated for successful descent at each level.

## Test Signals

Tests should build small vector trees and verify root lookup, nested lookup, missing paths, last-existing behavior, usage pointer return/null return, and malformed empty-vector handling if callers can provide it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh -->
