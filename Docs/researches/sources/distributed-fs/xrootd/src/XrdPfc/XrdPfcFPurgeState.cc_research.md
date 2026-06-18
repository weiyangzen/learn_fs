<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc

## Purpose

`XrdPfcFPurgeState.cc` implements file-level purge candidate discovery for XrdPfc. It traverses the cache namespace, identifies data files with matching `.cinfo` metadata, and keeps enough oldest or age-expired files to satisfy a requested purge size.

## Important APIs, Types, And Functions

- `FPurgeState::FPurgeState()` converts requested bytes to required 512-byte block count and initializes accumulators.
- `MoveListEntriesToMap()` moves unconditional list candidates into the time-sorted multimap.
- `CheckFile()` accounts file blocks and inserts candidates into either the age-expired list or LRU multimap.
- `ProcessDirAndRecurse()` scans current traversal files and descends into child directories.
- `TraverseNamespace()` creates `FsTraversal`, protects `pfc-stats`, and starts recursive traversal.

## Control Flow

During traversal, only entries with both data and `.cinfo` are considered. `CheckFile()` uses `.cinfo` mtime as access time. Files older than `m_tMinTimeStamp` go to `m_flist` with timestamp 0 and are counted immediately. Otherwise, the multimap keeps the oldest candidates until accumulated blocks reach the requested target; if too many blocks are held, newest candidates are removed from the map.

## State And Persistence

The object stores references to the OSS, requested/accumulated/total block counts, time thresholds, a list of age-expired candidates, and a time-sorted multimap of LRU candidates. This implementation does not unlink files; the commented `UnlinkInfoAndData()` shows older or planned unlink behavior.

## Dependencies And Integration Points

It depends on `XrdPfcFsTraversal`, `XrdPfcInfo`, `XrdPfcTrace`, `XrdOucEnv`, `XrdOucUtils`, `XrdOss`, and `XrdOssAt`. It feeds purge logic elsewhere with candidate lists/maps.

## Risks And Edge Cases

- Access time is derived from `.cinfo` mtime, so metadata timestamp accuracy controls LRU quality.
- Inconsistent pairs where data or `.cinfo` is missing are skipped, not repaired.
- `m_tMinUVKeepTimeStamp` is stored but not used in visible logic.
- `PurgeCandidate` path is built by concatenating traversal current path and filename; separator correctness depends on `FsTraversal`.
- Protected top directories are hard-coded to `pfc-stats`.

## Test Signals

Tests should cover candidate ordering, byte target trimming, age threshold list insertion, list-to-map movement, traversal with missing pairs, protected directory skipping, total block accounting, and zero/very small requested byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc -->
