# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurge.cc

## Purpose
Implements the legacy purge driver used by `ResourceMonitor` purge tasks. It builds purge candidate maps, optionally invokes a quota plugin, removes `.cinfo` and data files while respecting active/protected files, and reports purges back to resource monitoring.

## Important APIs, Types, and Functions
- `UnlinkPurgeStateFilesInMap(FPurgeState&, long long bytes_to_remove, const std::string& root_path)`: deletes oldest purge candidates until enough `st_blocks` are removed, skipping active or purge-protected files.
- `OldStylePurgeDriver(DataFsPurgeshot&)`: orchestrates plugin-driven per-directory purge and default namespace-wide purge.
- Uses `FPurgeState::TraverseNamespace()` and `MoveListEntriesToMap()` to gather candidates sorted by access time.

## Control Flow
`OldStylePurgeDriver` first asks a configured `PurgePin` for bytes to recover per directory and purges those directories. If space-based or age-based requirements remain, it creates a default `FPurgeState`, applies cold-file or uvkeep thresholds, traverses `/`, and deletes enough candidates. `UnlinkPurgeStateFilesInMap` derives data paths from `.cinfo` paths, checks active/protected status, unlinks info then data, decrements target blocks, and registers file purges.

## State and Persistence Behavior
This code persistently deletes local cache data and `.cinfo` metadata. It also updates resource-monitor state via purge registration. Candidate maps are transient. Files are skipped when active or purge-protected.

## Dependencies and Integration Points
Depends on `Cache`, `DataFsPurgeshot`, `ResourceMonitor`, `FPurgeState`, `PurgePin`, `Info::s_infoExtensionLen`, `XrdOss`, and trace macros. It is scheduled asynchronously by `ResourceMonitor::perform_purge_check`.

## Risks and Test Signals
Risks include deleting metadata before data, stale candidate maps racing with opens, path derivation by stripping `.cinfo`, and accounting mismatch if unlink/stat fails. Tests should cover active-file protection, quota plugin paths, age-based purge markers, uvkeep thresholds, failed traversal, missing data/info pairs, and resource-monitor purge accounting.
