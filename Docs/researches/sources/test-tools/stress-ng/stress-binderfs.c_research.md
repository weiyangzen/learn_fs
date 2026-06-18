<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-binderfs.c -->
# sources/test-tools/stress-ng/stress-binderfs.c

Purpose: `stress-binderfs.c` implements the privileged Linux `binderfs` stressor. It mounts binderfs, opens `binder-control`, creates many binder devices with `BINDER_CTL_ADD`, unlinks them, unmounts, and records mount/unmount latency.

Important APIs/types/functions: support depends on Linux Android binder and binderfs headers plus `CAP_SYS_ADMIN`. `stress_binderfs_supported()` probes binderfs by creating a temp directory and trying either the new mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`) or legacy `mount("binder", ..., "binder")`. `stress_binderfs_umount()` retries `umount()` for up to 15 seconds on `EBUSY`, then exercises duplicate and invalid unmount calls. `stress_binderfs()` owns the main mount/device/unmount loop.

Control flow: after temp directory setup and sync, each iteration mounts binderfs at a generated path, opens `binder-control`, optionally loops over 256 `BINDER_CTL_ADD` calls naming devices `sng-N`, unlinks the created device paths, closes control, unmounts with retry, and increments bogo operations. Error handling distinguishes unsupported/no-resource skip cases (`ENODEV`, `ENOSPC`, `ENOMEM`, `EPERM`) from hard failures.

State and persistence behavior: state includes the temp directory, transient binderfs mount, binder-control file descriptor, and created binder device nodes. Cleanup removes the stress-ng temp directory and unmounts on normal paths; stale mounts/device nodes are the key persistence risk after abnormal termination.

Dependencies and integration points: integrates with stress-ng temp-dir helpers, capability checks, filesystem path building, process states, metrics, and kernel binderfs ioctls. It registers a supported callback and `VERIFY_ALWAYS`; unavailable builds register `stress_unimplemented`.

Risks: privileged filesystem mutation and binder device creation can consume kernel resources. The supported probe may leave a mount if an intermediate new-mount-api step succeeds but later cleanup misses a state transition. `stress_binderfs()` sets `rc = EXIT_SUCCESS` before `clean`, which can override a break from an unmount failure path after the loop.

Test signals: cover systems without binderfs, without capability, with new and old mount APIs, with `BINDER_CTL_ADD` defined and absent, and with busy mounts requiring retry. Metrics are `microsecs per mount` and `microsecs per umount`; failures include inability to open `binder-control` or timed-out unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-binderfs.c -->
