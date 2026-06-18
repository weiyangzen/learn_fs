# sources/user-network-fs/samba/source3/modules/vfs_virusfilter.c

## Purpose
`vfs_virusfilter.c` is the front-end Samba VFS module for on-access antivirus scanning. It owns share-level configuration, selects one scanner backend (`clamav`, `dummy`, `fsav`, or `sophos`), hooks file open/close/delete/rename operations, evaluates scan results, optionally caches results, and applies configured infected-file actions such as quarantine, rename, delete, or command execution.

## Important APIs, Types, and Functions
The module registers `vfs_virusfilter_fns` via `vfs_virusfilter_init()`, with handlers for connect, disconnect, openat, close, unlinkat, and renameat. `virusfilter_vfs_connect()` reads `virusfilter:*` smb.conf parameters into `struct virusfilter_config`, builds include/exclude name arrays, prepares the socket I/O handle and optional memcache-backed result cache, creates the quarantine directory when needed, and initializes the selected backend. `virusfilter_scan()` is the central scanner wrapper. It checks the cache, invokes backend `scan_init`, `scan`, and `scan_end`, interprets `VIRUSFILTER_RESULT_*`, and dispatches remediation. `infected_file_action_quarantine()`, `infected_file_action_rename()`, and `infected_file_action_delete()` perform root-mediated VFS moves or unlink operations. `virusfilter_treat_infected_file()` and `virusfilter_treat_scan_error()` prepare environment variables and run configured shell commands.

## Control Flow
On connect, the module calls the next VFS connect first, allocates config, loads all options, creates helper objects, then initializes the backend. On open, it skips directories, named streams, disabled scan-on-open, truncating opens, non-regular files, files outside size limits, excluded paths, quarantine/rename trap names, then calls `virusfilter_scan()`. Infected scans fail open with the configured errno; scanner errors fail only when `block access on error` is enabled. On close, the next close runs before optional scan-on-close, and only modified regular files are scanned. Modified files invalidate cache entries when scan-on-close is disabled. Rename and unlink update or remove cache entries after successful filesystem changes.

## State and Persistence
Per-share state is talloc-owned `struct virusfilter_config` on the VFS handle. Persistent filesystem effects include quarantine directories/files, renamed files, deleted files, and optional external command side effects. The scan cache is process memory only, keyed by current directory plus file name and bounded by entry/time limits. Backend socket connections may persist across scans until `scan request limit` triggers `scan_end`.

## Dependencies and Integration Points
This file depends on Samba VFS, loadparm, talloc, SMB filename helpers, root privilege transitions, name matching, and the backend interface in `vfs_virusfilter_common.h`. It uses socket/cache/shell helpers from `vfs_virusfilter_utils.c`. It integrates with smbd file lifecycle semantics and must remain stackable by calling `SMB_VFS_NEXT_*` where appropriate.

## Risks
The module runs privileged filesystem operations and optional shell commands, so configuration validation and environment sanitization are security critical. Quarantine/rename checks are string based and depend on current path handling. Cache keys based on directory/name can become stale if file contents change without observed modified flags, though rename/unlink and modified close paths mitigate common cases. Scanning after close cannot prevent the completed write, only subsequent access or remediation. External scanner latency and socket failures directly affect file open/close behavior.

## Test Signals
Useful tests include backend selection failure without `virusfilter:scanner`, skip cases for directories/streams/truncating opens/size limits/exclude paths, cache add/get/rename/remove behavior, open/close errno behavior for infected and scanner-error results, quarantine tree creation with prefix/suffix validation, and command environment variables for infected and scan-error hooks.
