# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.h

Defines XFS sysctl tunable storage, legacy numeric IDs, and debug/global runtime settings.

Key structures:
- `xfs_sysctl_val_t` stores `min`, `val`, and `max`.
- `xfs_param_t` groups sysctl tunables for panic behavior, error reporting, sync timing, stats clearing, inherited inode flags, inode32 rotor behavior, filestream timeout, and blockgc scan interval.
- `struct xfs_globals` stores non-sysctl global runtime/debug settings:
  - Debug-only `pwork_threads` and `larp`
  - Btree bulk load slack values
  - Log recovery and mount delay values
  - `bug_on_assert`
  - `always_cow`

Other contents:
- Documents `xfs_error_level` behavior and panic-mask interaction.
- Keeps legacy numeric sysctl constants for historical ABI/indexing context.
- Declares `xfs_params` and `xfs_globals`.
- Provides real `xfs_sysctl_register/unregister` declarations under `CONFIG_SYSCTL`, otherwise no-op stubs.

Research notes:
- `xfs_globals` is consumed by sysfs debug knobs in `xfs_sysfs.c`, not by the sysctl table directly.
- The tunable wrapper makes sysctl validation table-driven through min/max pointers.
