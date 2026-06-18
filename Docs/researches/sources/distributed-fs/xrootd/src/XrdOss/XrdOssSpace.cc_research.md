# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.cc

## Purpose
Implements persistent cache-group usage accounting and quota-file loading for OSS cache spaces.

## Important APIs, types, and functions
Static members hold quota/usage filenames, update filename, in-memory `uEnt` table, active-entry vector, free entry, usage fd, sync counters, solitary flag, and last modification times. `Adjust()` updates a group usage field (`Serv`, `Pstg`, `Purg`, or `Admin`), using file locks for non-server updates and converting solitary server changes to post-stage/purge fields. `Assign()` finds or creates a usage entry for a cache group and returns its index. `Init()` configures quota and usage files, creates `.Usage`/`.Usage.upd`, reads or initializes the fixed-size table, and exports file paths to the environment. `Quotas()` reloads the quota file when mtime changes and updates matching `XrdOssCache_Group` quota fields. `Readjust()` rereads the usage file when the update marker changes and merges pending staged/purged/admin adjustments into server usage. `Unassign()` clears a group entry. `Usage()` overloads return counters with optional reread. `UsageLock()` wraps blocking `fcntl` file locks.

## Control flow
Configuration calls `Init()` then `XrdOssCache::Init()` assigns cache groups. Runtime operations call `Adjust()` for size changes. The cache scan thread calls `Quotas()` and `Readjust()` to refresh quotas and reconcile usage deltas from other processes.

## State and persistence
Persistence is the fixed-size `.Usage` file plus `.Usage.upd` marker and optional quota file. Updates use positional reads/writes into `uEnt` records, optional fsync batching, and file locks to coordinate multiprocess access. In-memory state mirrors active records.

## Dependencies and integration points
Depends on `XrdOssCache_Group`, `XrdOuca2x`, `XrdOucEnv`, `XrdOucStream`, `XrdOucUtils::InstName`, `XrdSysFD_Open`, and OSS logging. The quota file directly names cache groups configured in `XrdOssCache`.

## Risks and test signals
The fixed-size table can fill, `Unassign()` appears to write from `uData[freeEnt]` after clearing `uData[i]`, and `UsageLock()` has a local static mutex shadowing the namespace mutex in a confusing way. Tests should cover fresh and existing usage files, invalid file size, concurrent adjust/readjust, sync batching, solitary conversions, quota reload mtime behavior, unknown quota groups, table overflow, and unassign correctness.
