# sources/test-tools/xfstests/common/dmdust

Purpose: common xfstests helpers for device-mapper dust fault-injection devices.

Important APIs: exports `DUST_NAME="dust-test.$seq"` and defines `_init_dust`, `_mount_dust`, `_unmount_dust`, and `_cleanup_dust`.

Control flow: `_init_dust` gets scratch device sector count, builds a dust table mapping the scratch device with 512-byte sector size, and creates `/dev/mapper/$DUST_NAME` through `_dmsetup_create`. `_mount_dust` computes scratch mount options and mounts `$DUST_DEV` at `$SCRATCH_MNT`. `_cleanup_dust` resumes the mapper in case a load failed, unmounts scratch best-effort, and removes the mapper.

State and dependencies: creates a device-mapper target and mounts it. Depends on `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$FSTYP`, dmsetup helpers from other common files, and mount/unmount wrappers.

Integration points: tests can source this helper to inject read/write dust behavior on scratch filesystems.

Risks and test signals: cleanup must run even after partial setup to avoid hung unmounts. Device-mapper target availability is required. Tests should validate mapper creation/removal and cleanup after simulated load failure.
