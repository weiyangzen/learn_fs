# sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests

Purpose: local QEMU/KVM runner for xfstests. It prepares rootfs/test disks, stages updated test artifacts/modules, configures networking/virtfs, launches QEMU with the selected kernel, captures logs, and extracts result archives.

Important flow/options: handles `install-kconfig`, `kbuild`, and `setup` passthroughs; sources config and CLI parsing; downloads rootfs if missing; optionally builds kernel; validates kernel and test disks; configures networking, logs/results filenames, virtiofs/9p shares, modules and update tarballs, architecture-specific QEMU machine/console, and then runs `qemu-system-*`.

Control flow: creates a temporary VDH tar image as a communication disk, optionally appends xfstests/extra/files/modules tarballs, truncates it to 256M, starts QEMU with rootfs plus many virtio disks and metadata kernel args, tees serial output to log, extracts `exit_code` and `results.tar.xz` from VDH after VM exit, trims log summary, restores terminal line wrap, and exits with guest-provided status.

State/persistence: may download rootfs into `test-appliance`, create/update test disks via setup utility, create logs under `$DIR/logs`, results tarballs, temp VDH and extraction dirs, virtfs dirs under `/tmp`, and virtiofsd sockets/logs.

Dependencies/integration: depends on QEMU/KVM, kvm-do-setup, parse_cli config, kernel/modules artifacts from kbuild, rootfs image, tar, xz, wget, virtiofsd, and host network/tap setup.

Risks: powerful local VM command with many unquoted variable expansions from config. Virtiofsd background processes are started without explicit cleanup in this script. Rootfs download URL and qemu feature flags are host-sensitive. There is a typo in the scratch path default branch assigning `VIRTFS_SCRATCH_PATH` when checking `VIRTFS_SCRATCHTEST_PATH`.

Test signals: no-action command inspection, setup-created disks, successful boot/log/result extraction, and virtfs/9p specific configs are key validations.
