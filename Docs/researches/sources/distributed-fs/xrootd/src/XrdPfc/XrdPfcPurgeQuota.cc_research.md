# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgeQuota.cc

## Purpose
Implements a `PurgePin` plugin that enforces directory byte quotas from a configuration file. It computes bytes to recover for each configured directory by comparing snapshot usage with configured quotas.

## Important APIs, Types, and Functions
- `class XrdPfcPurgeQuota : public XrdPfc::PurgePin`.
- `InitDirStatesForLocalPaths()` resolves each configured path to a `DirUsage` entry in the purge snapshot.
- `GetBytesToRecover()` computes `512 * st_blocks - quota` for each directory and returns total positive excess.
- `ConfigPurgePin()` parses a quota file where each line contains a directory path and quota, accepting size suffixes through `XrdOuca2x::a2sz`.
- `extern "C" XrdPfcGetPurgePin()` exports the plugin factory.

## Control Flow
Configuration opens the quota file, captures plugin-specific config lines, reads path/quota pairs, converts quota values, and appends `DirInfo` records. During purge, snapshot lookup populates `dirUsage`; missing dirs log errors and are skipped; excess bytes become `nBytesToRecover` for the old purge driver.

## State and Persistence Behavior
The plugin stores configured quotas in memory. It does not delete files directly. Persistent effects occur when `OldStylePurgeDriver` consumes the computed recovery list.

## Dependencies and Integration Points
Depends on `PurgePin`, `DataFsPurgeshot`, `XrdOucEnv`, `XrdOucStream`, `XrdOuca2x`, and `XrdSysError` logging. It integrates as a dynamically loaded purge plugin through `XrdPfcGetPurgePin`.

## Risks and Test Signals
Risks include continuing after quota file open failure, accepting invalid or duplicate paths, units conversion ambiguity, and quota paths not found in the snapshot. Tests should cover missing file, malformed lines, suffix and raw integer quotas, missing directories, and multiple quotas summing recovery bytes.
