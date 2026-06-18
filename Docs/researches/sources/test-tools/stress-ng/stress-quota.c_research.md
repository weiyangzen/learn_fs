# sources/test-tools/stress-ng/stress-quota.c research

Purpose: implements `quota`, a Linux OS stressor that locates mounted block devices and exercises quota control commands through `quotactl` and optionally `quotactl_fd`.

Important APIs, types, and functions: `stress_dev_info_t` associates mountpoints with `/dev` block device paths and skip state. `quotactl_status_t` accounts error categories. `do_quotactl_call()` randomly chooses `shim_quotactl_fd()` or classic `quotactl()`, disabling fd mode after `ENOSYS`. `do_quotas()` issues available `Q_GETQUOTA`, `Q_GETNEXTQUOTA`, `Q_GETFMT`, `Q_GETINFO`, `Q_GETSTATS`, `Q_SYNC`, and invalid argument probes.

Control flow: `stress_quota_supported()` requires `CAP_SYS_ADMIN`. `stress_quota()` reads mounts, scans `/dev` for block devices whose `st_rdev` matches mount `st_dev`, deduplicates devices, synchronizes, and loops over candidates. Devices that consistently return unsupported, read-only, not-block, or not-enabled statuses are skipped. Complete failure or privilege errors abort; otherwise bogo ops advance per pass.

State and persistence: only transient mount/device tables and duplicated device names are stored. Quota commands are read/sync oriented plus invalid probes; no intended persistent quota changes are made.

Dependencies and integration: Linux-only, requires `sys/quota.h` and at least one quota command macro. Uses stress-ng capabilities and mount helpers. Metadata includes supported callback, `CLASS_OS`, and `VERIFY_ALWAYS`.

Risks: requires elevated capability and real block-device/mount discovery; containers may expose no suitable devices. Error classification determines whether to skip or fail, so filesystem-specific errno behavior matters. `Q_SYNC` can have system-wide effects.

Test signals: capability skip, candidate device discovery, per-device skip transitions, quota error accounting, and bogo increments when devices are exercised.
