# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_root.c

## Role
Implements the `vdev_ops_t` vector for the pool root vdev. The root vdev is an aggregate/non-leaf node, so its main responsibilities are opening/closing children and translating child failure counts into root-vdev health.

## Main Logic
- `vdev_root_core_tvds()` counts core top-level children, excluding holes, log devices, and indirect vdevs.
- `too_many_errors()` decides whether the root vdev must become unavailable. It tolerates no errors when all core top-level vdevs are failed and otherwise compares against `spa_missing_tvds_allowed()`.
- `vdev_root_open()` rejects an empty root with `VDEV_AUX_BAD_LABEL`, opens children, counts non-log child open errors, records missing top-level vdevs during pool load, and fails with `VDEV_AUX_NO_REPLICAS` if the error policy is exceeded.
- `vdev_root_close()` closes every child vdev.
- `vdev_root_state_change()` maps aggregate `faulted`/`degraded` counts to `CANT_OPEN`, `DEGRADED`, or `HEALTHY`.

## Interfaces And Dependencies
- Defines global `vdev_root_ops` with no I/O start/done methods because I/O is never issued directly to the root vdev.
- Depends on SPA load state, missing-tvds accounting, and generic vdev open/close/state helpers.
- Uses `vdev_indirect_ops` exclusion to avoid treating removed/indirect mapping vdevs as core redundancy members.

## Important Details
- Log-device open errors are ignored when deciding root availability.
- `ASSERT3U(numerrors, <=, tvds)` encodes the expectation that counted errors are only among core top-level vdevs.
- The policy is intentionally conservative: losing all core top-level vdevs is fatal; other tolerance is delegated to SPA missing-tvds policy.
