# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_quota.c

## Summary
Implements optional VFS-level in-memory space accounting and quota-like limit checks by mount, UID, and GID.

## Main Responsibilities
- Maintains per-mount UID and GID accounting trees keyed by ID chunks.
- Enables accounting via `vfs.quota_enabled`.
- Initializes per-mount accounting in `vq_init()`.
- Accounts byte deltas through `vfs_stdaccount()`.
- Implements `sys_vquotactl()` commands for usage export/import and limit setting.
- Selects a valid accounting mount for vnodes with `vq_vptomp()`.
- Checks whether a write is within global, UID, and GID limits with `vq_write_ok()`.

## Important Behavior
Accounting stores total bytes plus per-UID/per-GID chunk arrays in red-black trees. Updates are protected by `mp->mnt_acct.ac_spin`. The userland control interface uses proplib dictionaries and arrays with commands such as `get usage all`, `set usage all`, `set limit`, `set limit uid`, and `set limit gid`.

`vq_write_ok()` treats limit `0` as unlimited. It checks mount-wide limit first, then UID limit, then GID limit.

## Risks
`vq_done()` is a TODO and does not free accounting trees. The code comments call out UID/GID duplication and a potentially stale `v_pfsmp` pointer, mitigated only by `mountlist_exists()`. `sys_vquotactl()` has limited validation and several paths return without releasing all proplib objects.
