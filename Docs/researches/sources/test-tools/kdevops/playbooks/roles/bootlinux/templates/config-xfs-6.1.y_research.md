<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y -->
# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y

Source read: complete file, 6081 lines, 161852 bytes, sha256 `ca34467e30860d28`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y_research.md`.

Purpose: static Linux 6.1 kernel `.config` template for the kdevops bootlinux role, tuned around XFS test guests. It fixes compiler/toolchain assumptions, x86_64 virtualization support, block/storage features, filesystem modules, tracing, and debug/fault-injection behavior for reproducible kernel builds.

Important APIs/types/functions: this is declarative Kconfig data rather than executable code. High-signal settings include `CONFIG_X86_64=y`, `CONFIG_MODULES=y`, `CONFIG_PREEMPT=y`, `CONFIG_CGROUPS=y`, `CONFIG_IO_URING=y`, `CONFIG_BLOCK=y`, `CONFIG_BLK_DEV_ZONED=y`, `CONFIG_BLK_DEBUG_FS=y`, `CONFIG_XFS_FS=m`, `CONFIG_XFS_QUOTA=y`, `CONFIG_XFS_POSIX_ACL=y`, `CONFIG_XFS_RT=y`, `CONFIG_XFS_DEBUG=y`, `CONFIG_EXT4_FS=m`, `CONFIG_BTRFS_FS=m`, `CONFIG_KVM=m`, `CONFIG_VIRTIO_BLK=m`, `CONFIG_NVME_*`, `CONFIG_DM_*`, `CONFIG_MD_RAID*`, and `CONFIG_CXL_*`.

Control flow: the bootlinux workflow consumes the file as a kernel configuration seed, normally copying or merging it into the Linux source tree before build. There are no branches at runtime in this file; behavior emerges when Kconfig, `make`, module packaging, bootloader setup, and initramfs handling interpret these symbols.

State and persistence behavior: the selected symbols persist into the built kernel image, generated modules, `/proc/config.gz` when `CONFIG_IKCONFIG_PROC=y`, and boot/runtime capabilities. XFS, ext4, btrfs, KVM, virtio, NVMe, SCSI, CXL, DM, and MD support are mostly modular, so module availability and initramfs contents determine what is usable at boot.

Dependencies and integration: tied to GCC/binutils style x86_64 builds (`CONFIG_CC_IS_GCC=y`, GCC 11.3 in the captured text), kdevops VM boot flows, storage tests, block debugfs/fault-injection tooling, QEMU/KVM guests, virtio devices, NVMe fabrics/target tests, and CXL/pmem workflows. NFS is disabled, so NFS workflows need another config.

Risks: XFS debug and broad tracing add overhead and can change timing-sensitive filesystem tests. XFS online scrub is disabled. btrfs lacks POSIX ACL, integrity, sanity, debug, assert, and ref-verify settings, so it is not a maximal btrfs debug kernel. NFS client/server support is absent. Modular storage drivers can break early root/data-device discovery if not included in initramfs.

Test signals: useful validation is `scripts/config` or `make olddefconfig` stability, successful boot under the target QEMU/KVM profile, `/proc/config.gz` matching the template intent, `modprobe xfs btrfs ext4 virtio_blk nvme cxl_mem`, mounting XFS with quotas/ACL/rt where expected, and running storage tests that exercise block debugfs, fail-make-request, dm-log-writes, and XFS debug paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-6.1.y -->
