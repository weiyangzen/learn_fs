# sources/test-tools/stress-ng/stress-statmount.c

## Purpose

`stress-statmount.c` implements `statmount`, a Linux filesystem/OS stressor for the newer `statmount` and `listmount` syscalls. It finds the unique mount ID for `/`, repeatedly stats that root mount, lists mount IDs under the root mount tree, stats each listed mount with mount and superblock masks, and reports call rate.

## Important APIs, Types, and Functions

- `shim_statmount()` wraps `syscall(__NR_statmount)` using `struct mnt_id_req`.
- `shim_listmount()` wraps `syscall(__NR_listmount)` using the same request structure.
- `stress_statmount_statroot()` calls `statmount` on the root mount ID, measures duration, verifies returned structure size and mount ID, and counts one call.
- `stress_statmount_listroot()` calls `listmount(LSMT_ROOT, ...)`, tracks the maximum returned mount count, and stats every returned mount with `STATMOUNT_MNT_BASIC` and `STATMOUNT_SB_BASIC`.
- `stress_statmount()` probes syscall availability, uses `shim_statx()` with `STATX_MNT_ID_UNIQUE` to get `/`'s mount ID, runs the loop, prints max mount points, and emits "statmount calls per sec".

## Control Flow

At startup, the stressor calls `shim_statmount(0, 0, NULL, 0, 0)` as an availability probe and skips if `ENOSYS`. It then calls `shim_statx(AT_FDCWD, "/", 0, STATX_MNT_ID_UNIQUE, &sx)` to retrieve the unique mount ID for root. After synchronization, each loop verifies the root mount via `stress_statmount_statroot()`, lists root mount descendants into a fixed 1024-entry array, stats each listed mount with both mount and superblock masks when successful, increments bogo operations, and continues until stopped. At the end instance zero reports the maximum mount count and metrics are recorded from accumulated duration/count.

## State and Persistence Behavior

The stressor only reads mount metadata through syscalls. It stores local timing counters and maximum mount count. No files are created, no mount table changes are made, and no state persists after exit.

## Dependencies and Integration Points

The file is guarded on Linux syscall numbers and mount/statx constants: `__NR_statmount`, `__NR_listmount`, `__NR_statx`, `MNT_ID_REQ_SIZE_VER0`, `STATMOUNT_*`, `STATX_MNT_ID_UNIQUE`, and `LSMT_ROOT`. It integrates with stress-ng `shim_statx`, state transitions, metrics, and logging. Unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The syscall ABI is relatively new, so headers may expose constants on systems whose running kernel returns `ENOSYS`; the runtime probe handles that. `listmount()` can return more than 1024 entries, but this stressor requests a bounded list and tracks only the returned count. Individual `statmount()` calls for listed IDs can fail due to races with mount changes and are ignored in `stress_statmount_listroot()`, while root stat failures are fatal. The skip log for failed `statx` is missing a trailing newline in the source.

## Test Signals

Expected signals include skip behavior on older kernels, successful root mount ID verification on supported kernels, instance-zero mount count logging, and "statmount calls per sec" metrics. Tests should include mount namespace environments with small and large mount tables and concurrent mount churn to exercise ignored per-mount races.
