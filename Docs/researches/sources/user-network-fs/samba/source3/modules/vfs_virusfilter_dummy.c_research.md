# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_dummy.c

## Purpose
The dummy backend provides a scanner implementation for tests and controlled deployments. It marks files infected when their path matches the configured `virusfilter:infected files` list and clean otherwise.

## Important APIs, Types, and Functions
`virusfilter_dummy_scan()` logs the file being scanned and calls `is_in_path(fsp->fsp_name->base_name, config->infected_files, false)`. It returns `VIRUSFILTER_RESULT_INFECTED` on match and `VIRUSFILTER_RESULT_CLEAN` otherwise. `virusfilter_dummy_init()` allocates a backend named `dummy` with only the `scan` callback set.

## Control Flow
The core calls this backend exactly like a real scanner. There is no connection setup, no scan initialization, and no scan teardown. Result handling, cache insertion, blocking behavior, and remediation all stay in `vfs_virusfilter.c`.

## State and Persistence
The backend stores no private state and does not set a report string. It depends on the config's `infected_files` pattern list, which is built from smb.conf at connect time. Persistence occurs only through the core's normal infected-file action.

## Dependencies and Integration Points
It includes `vfs_virusfilter_utils.h`, which brings in common types and Samba path matching. It is built into the `vfs_virusfilter` module with the other backends.

## Risks
Because `reportp` is not populated, downstream infected reporting can see a null report and must tolerate it. The backend is intentionally not a real scanner; enabling it outside test scenarios would only enforce administrator-provided path patterns.

## Test Signals
Tests should configure `virusfilter:scanner = dummy` with matching and non-matching `infected files` patterns, then assert open/close behavior, remediation paths, cache handling, and null-report tolerance.
