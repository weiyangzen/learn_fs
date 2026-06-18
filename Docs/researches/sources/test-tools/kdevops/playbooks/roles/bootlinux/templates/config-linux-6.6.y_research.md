# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-linux-6.6.y

## Purpose

`sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-linux-6.6.y` is a generated Linux/x86 kernel `.config` snapshot for a Linux 6.6.0-rc2 kernel. It is stored as a kdevops `bootlinux` role template so automation can build a repeatable x86_64 test kernel from a selected Linux tree instead of inheriting a host distribution configuration.

The file is declarative Kconfig state, not executable source code. In this snapshot it contains 6,091 lines: 1,746 built-in `=y` symbols, 563 module `=m` symbols, 2,588 explicitly disabled symbols, 27 string assignments, and 86 numeric assignments. The profile is broad and test-oriented: x86_64 SMP, preemption, cgroups, namespaces, initrd, modules, virtualized guests, storage stacks, common filesystem modules, debugfs, tracing, fault injection, and XFS debug/online repair are enabled.

## Important APIs, Types, And Symbols

The source-level interface is the Linux Kconfig `.config` grammar: `CONFIG_FOO=y` for built-ins, `CONFIG_FOO=m` for modules, `# CONFIG_FOO is not set` for disabled options, plus string and numeric assignments. The consuming API is the `bootlinux` Ansible role, where `target_linux_config` defaults to `config-{{ target_linux_ref }}` and `tasks/config.yml` searches `templates/config-kdevops`, `templates/{{ target_linux_config }}`, and the newest `config-next-*` fallback before setting `linux_config`.

Key enabled symbols define the intended environment:

- Build and boot identity: `CONFIG_CC_IS_GCC=y`, GCC 13.2.0 metadata, `CONFIG_KERNEL_XZ=y`, `CONFIG_BLK_DEV_INITRD=y`, `CONFIG_BOOT_CONFIG=y`, `CONFIG_IKCONFIG=y`, and `CONFIG_IKCONFIG_PROC=y`.
- Architecture and virtualization: `CONFIG_64BIT=y`, `CONFIG_X86_64=y`, `CONFIG_SMP=y`, `CONFIG_NR_CPUS=512`, `CONFIG_HYPERVISOR_GUEST=y`, `CONFIG_KVM_GUEST=y`, `CONFIG_KVM=m`, `CONFIG_KVM_INTEL=m`, `CONFIG_KVM_AMD=m`, `CONFIG_XEN=y`, `CONFIG_XEN_DOM0=y`, and Hyper-V guest modules.
- Runtime model: `CONFIG_PREEMPT=y`, `CONFIG_PREEMPT_DYNAMIC=y`, `CONFIG_NO_HZ_IDLE=y`, `CONFIG_HIGH_RES_TIMERS=y`, `CONFIG_CPU_ISOLATION=y`, cgroups, cpusets, user/pid/net/time/ipc namespaces, and `CONFIG_IO_URING=y`.
- Module ABI: `CONFIG_MODULES=y`, `CONFIG_MODULE_UNLOAD=y`, forced load/unload support, `CONFIG_MODVERSIONS=y`, and no module signature requirement.
- Storage and block testing: blk-mq, zoned block support, block debugfs, `null_blk` with fault injection, loop, RAM disk, virtio-blk, NVMe host/fabrics/target modules, SCSI debug, MD RAID, bcache, device mapper targets including dm-flakey, dm-delay, dm-log-writes, dm-integrity, and dm-zoned.
- Filesystems: `EXT4_FS=m`, `XFS_FS=m`, `BTRFS_FS=m`, `F2FS_FS=m`, `ZONEFS_FS=m`, `FS_DAX=y`, quota, fscrypt, fanotify/inotify, tmpfs, hugetlbfs, NFS/NFSD modules, and 9P filesystem support.
- XFS test surface: `CONFIG_XFS_DEBUG=y`, `CONFIG_XFS_ASSERT_FATAL=y`, `CONFIG_XFS_ONLINE_SCRUB=y`, `CONFIG_XFS_ONLINE_SCRUB_STATS=y`, and `CONFIG_XFS_ONLINE_REPAIR=y`.
- Observability and fault testing: `CONFIG_DEBUG_FS=y`, `CONFIG_DYNAMIC_DEBUG=y`, `CONFIG_DEBUG_INFO=y`, ftrace/function graph tracing, kprobe/uprobe events, BPF events, block I/O tracing, kmemleak, lockup/hung-task detectors, `CONFIG_FAULT_INJECTION=y`, `CONFIG_FAIL_MAKE_REQUEST=y`, `CONFIG_FAIL_FUNCTION=y`, and `CONFIG_TEST_KMOD=m`.

## Control Flow

This file has no runtime control flow by itself. Its control effect happens through the bootlinux build pipeline:

1. kdevops resolves `target_linux_config`, normally from the selected kernel ref.
2. `roles/bootlinux/tasks/config.yml` builds a template search list and records the chosen basename as `linux_config`.
3. The builder, target-node, or 9P build path copies this template into the Linux source tree as `.config` unless config fragments are enabled.
4. The role runs Kconfig reconciliation, typically `yes "" | make oldconfig` for monolithic configs in 9P/target flows, accepting defaults for symbols not represented by this snapshot.
5. The configured tree is compiled and installed according to `target_linux_make_cmd` and related role variables.

At kernel runtime, the control flow belongs to compiled Linux subsystems. This config biases that runtime toward virtualized x86_64 test nodes with module-loadable storage/filesystem drivers and rich debug/tracing controls.

## State And Persistence

The template is persistent repository state. During a bootlinux run it is copied to a mutable `.config` under `target_linux_dir_path` or `bootlinux_9p_host_path`; Kconfig may then rewrite it during `oldconfig`. Build outputs persist as kernel images, modules, package artifacts, and installed `/lib/modules/<kernelrelease>` content.

Runtime state exposed by the resulting kernel includes `/proc/config.gz` through `IKCONFIG_PROC`, debugfs/tracefs controls, dynamic debug state, kmemleak state, fault-injection knobs, pstore records, module load state, and filesystem/block state for mounted test devices. Because many storage and filesystem features are modules, the installed module tree and initramfs contents are part of the effective persisted behavior.

## Dependencies

Build dependencies come from the Linux kernel and kdevops bootlinux role: an x86_64 Linux tree compatible with this 6.6-era Kconfig snapshot, GCC/binutils-compatible toolchain, make, role-installed build dependencies, optional ccache/reproducible-build environment variables, and enough disk space for a debug-capable kernel with many modules.

Runtime dependencies include a boot path that can reach the root filesystem, module installation matching the booted kernel, and matching virtual hardware. Virtio block/network/console, NVMe, SCSI disks, ext4, XFS, Btrfs, F2FS, and 9P are modules, so initramfs or post-boot module loading must supply what the deployment needs. 9P workflows depend on `NET_9P`, `NET_9P_VIRTIO`, `9P_FS`, and the libvirt/QEMU mount tag generated by kdevops.

## Integration Points

The direct integration point is `sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/`, where sibling `config-*` files define other kernel baselines. `playbooks/roles/bootlinux/defaults/main.yml` defines `target_linux_config`, build paths, make commands, ccache/reproducible environment, 9P mode, and fragment mode. `tasks/config.yml` selects this file, and build tasks copy it as `.config`.

The file also integrates indirectly with kdevops workflows:

- `workflows/linux/Makefile` and `playbooks/bootlinux.yml` drive the bootlinux role.
- 9P and guestfs generation rely on enabled 9P and virtio support.
- fstests and block tests rely on ext4/XFS/Btrfs/F2FS, quota, fscrypt, DAX, dm targets, null_blk, SCSI debug, NVMe, and fault injection.
- Existing fstests expunge files mention failures or required coverage after enabling `CONFIG_XFS_DEBUG`, which is enabled in this profile.

## Risks And Edge Cases

The header says the file is automatically generated; manual edits are fragile unless the intent is to change the stored baseline. The filename says `config-linux-6.6.y`, but the embedded header is `Linux/x86 6.6.0-rc2`; applying it to later stable 6.6.y trees relies on `make oldconfig` defaults and may silently alter behavior as Kconfig symbols change.

Boot viability is sensitive to modules. Several common boot-relevant drivers are not built in, including virtio block, virtio net, virtio console, NVMe, SCSI disk, ext4, XFS, Btrfs, F2FS, and 9P. A missing initramfs or mismatched module install can produce a kernel that builds successfully but cannot boot or cannot run the intended tests.

The debug/test profile is intentionally heavy. `DEBUG_FS_ALLOW_ALL`, dynamic debug, ftrace, kmemleak, fault injection, XFS debug assertions, module force loading/unloading, and unrestricted debugfs are useful in a lab but add overhead and attack surface. `CONFIG_KUNIT` and `CONFIG_KCOV` are disabled, so unit-test and coverage workflows need a different config or fragment overlay.

Feature coverage is broad but not universal. FUSE, overlayfs, CIFS/SMB server, CephFS, USB storage, xHCI, VFIO, vhost, and many network emulation/qdisc options are disabled. Tests assuming those capabilities will skip, fail, or require a different template.

## Test Signals

Good validation signals are:

- The bootlinux log selects `config-linux-6.6.y` as `linux_config` when the workflow asks for this baseline and no `config-kdevops` override exists.
- The copied `.config` runs through `make oldconfig` without unexpected Kconfig warnings.
- The kernel and modules build and install successfully, with `/lib/modules/<kernelrelease>` populated.
- A booted node reports the intended kernel with `uname -r` and exposes `/proc/config.gz`.
- `/proc/config.gz` contains sentinel symbols such as `CONFIG_X86_64=y`, `CONFIG_PREEMPT_DYNAMIC=y`, `CONFIG_IKCONFIG_PROC=y`, `CONFIG_MODULES=y`, `CONFIG_VIRTIO=m`, `CONFIG_9P_FS=m`, `CONFIG_EXT4_FS=m`, `CONFIG_XFS_FS=m`, `CONFIG_XFS_DEBUG=y`, `CONFIG_FAULT_INJECTION=y`, and `CONFIG_DEBUG_FS=y`.
- Test nodes can load expected modules such as `virtio_blk`, `virtio_net`, `9p`, `9pnet_virtio`, `ext4`, `xfs`, `btrfs`, `f2fs`, `null_blk`, `scsi_debug`, `dm_flakey`, `dm_log_writes`, `nvme`, and `nvmet`.
- debugfs and tracefs mount successfully, and fault-injection, dynamic debug, ftrace, kmemleak, and block tracing interfaces are visible when tests require them.
