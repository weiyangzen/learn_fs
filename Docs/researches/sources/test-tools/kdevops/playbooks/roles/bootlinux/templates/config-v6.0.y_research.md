# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-v6.0.y

## Purpose
`config-v6.0.y` is a full Linux kernel `.config` template for the kdevops `bootlinux` Ansible role. It targets Linux/x86 6.0.9 on x86_64 and acts as the seed configuration copied into a checked-out kernel tree as `.config` before `oldconfig`/`olddefconfig` and build execution. The file is static Kconfig data, not executable code: it contains no Jinja conditionals despite living in an Ansible `templates/` directory.

The configuration is broad and guest-oriented. It enables x86_64, SMP, preemptible kernel behavior, cgroups, namespaces, initrd support, module support, KVM/Xen/Hyper-V/virtio guest support, large storage stacks, extensive networking, tracing, debugfs, kmemleak, ftrace, and fault-injection hooks. It keeps some network and filesystem surfaces intentionally absent, including NFS, NFSD, Ceph FS/lib, CIFS/SMB, overlayfs, fuse, vhost, VFIO, USB storage, AHCI, and many physical NIC drivers.

## Important Kconfig Interfaces
- Build identity and compiler assumptions: `CONFIG_CC_IS_GCC=y`, GCC 11.3/binutils 2.38 metadata, `CONFIG_KERNEL_XZ=y`, `CONFIG_LOCALVERSION=""`, `CONFIG_BUILD_SALT="4.19.0-1-amd64"`, and disabled `CONFIG_LOCALVERSION_AUTO`.
- Boot and runtime base: `CONFIG_BLK_DEV_INITRD=y`, all common initramfs decompressors, `CONFIG_BOOT_CONFIG=y`, `CONFIG_IKCONFIG=y`, `CONFIG_IKCONFIG_PROC=y`, `CONFIG_KALLSYMS_ALL=y`, `CONFIG_PROC_FS=y`, `CONFIG_SYSFS=y`, `CONFIG_TMPFS=y`, and `CONFIG_CONFIGFS_FS=m`.
- Scheduler and isolation: `CONFIG_PREEMPT=y`, `CONFIG_PREEMPT_DYNAMIC=y`, `CONFIG_HZ_250=y`, `CONFIG_NO_HZ_IDLE=y`, `CONFIG_HIGH_RES_TIMERS=y`, `CONFIG_CPU_ISOLATION=y`, `CONFIG_NUMA=y`, `CONFIG_NUMA_BALANCING_DEFAULT_ENABLED=y`, and `CONFIG_NR_CPUS=512`.
- Container/namespace support: `CONFIG_CGROUPS=y`, memory/block/cpu/pids/freezer/device/perf/BPF cgroups, `CONFIG_NAMESPACES=y`, `CONFIG_USER_NS=y`, `CONFIG_PID_NS=y`, and `CONFIG_NET_NS=y`.
- Virtualization: `CONFIG_HYPERVISOR_GUEST=y`, `CONFIG_KVM_GUEST=y`, `CONFIG_KVM=m`, `CONFIG_KVM_INTEL=m`, `CONFIG_KVM_AMD=m`, Xen guest/dom0 support, Hyper-V modules, virtio PCI/block/net/console/balloon/mem/pmem/input/MMIO modules, 9p net transport modules, and `CONFIG_9P_FS=m`.
- Storage and filesystems: modular NVMe host/fabrics/target, modular SCSI, virtio SCSI/block, null_blk, loop, nbd, zram, md/raid, bcache, device mapper targets, iSCSI target, ext2/3/4, XFS, Btrfs, F2FS, zonefs, DAX/libnvdimm/CXL support, FAT/exFAT/UDF/ISO9660, and quota/fsnotify.
- Networking: IPv4/IPv6, multicast/routing, netfilter/nftables/xtables as modules, bridge as module, TUN/VETH/virtio-net, WireGuard, RDMA/InfiniBand stack, vsock, 9p net, and core BPF syscall/JIT support.
- Security and crypto: seccomp/filter, stack protector strong, kernel/module signature infrastructure, AppArmor default, SELinux/TOMOYO/Yama enabled, integrity framework without IMA/EVM, broad crypto algorithms, FIPS API flag, and signed PE verification.
- Debug/test instrumentation: `CONFIG_DEBUG_KERNEL=y`, `CONFIG_DEBUG_INFO=y`, `CONFIG_DEBUG_FS=y`, `CONFIG_DYNAMIC_DEBUG=y`, `CONFIG_DEBUG_KMEMLEAK=y`, `CONFIG_FTRACE=y`, function graph tracing, kprobe/uprobe/BPF events, block I/O tracing, fault injection, `CONFIG_FAIL_MAKE_REQUEST=y`, `CONFIG_FAIL_FUNCTION=y`, and test modules such as `CONFIG_TEST_LKM=m`, `CONFIG_TEST_FIRMWARE=m`, `CONFIG_TEST_SYSCTL=m`, and `CONFIG_TEST_KMOD=m`.

## Control Flow
This file has no internal control flow. The effective flow comes from the `bootlinux` role:

1. `tasks/config.yml` builds a search list containing `templates/config-kdevops`, `templates/{{ target_linux_config }}`, and the newest `config-next-*` fallback, then sets `linux_config` with `with_first_found`.
2. `tasks/build/targets.yml` or `tasks/build/builder.yml` copies `{{ linux_config }}` from the role templates directory into `{{ target_linux_dir_path }}/.config`.
3. Non-fragment builds run `oldconfig`/`olddefconfig`, allowing the kernel tree to reconcile this static 6.0-era config with the checked-out kernel version.
4. The kernel build runs with GCC or LLVM settings from role variables. The produced kernel, modules, packages, and installed boot artifacts are downstream effects of the copied `.config`, not state maintained by this file.

When `bootlinux_use_config_fragments` is true for applicable paths, `config-fragments.yml` instead invokes `scripts/kconfig/merge_config.sh`; in that mode this full template may be bypassed in favor of selected upstream and kdevops fragments.

## State and Persistence Behavior
The template itself is immutable source data. Its persistent effects appear after Ansible copies it to a Linux source checkout as `.config`, after Kconfig rewrites `.config` during `oldconfig`/`olddefconfig`, and after the kernel build emits `.config`, generated headers, modules, vmlinux/bzImage, packages, and install artifacts.

State-sensitive choices include module signing (`CONFIG_MODULE_SIG=y` with an empty `CONFIG_MODULE_SIG_KEY`, causing the kernel build to use or generate the normal signing key material), `/proc/config.gz` exposure through `IKCONFIG_PROC`, debugfs/tracing/fault-injection interfaces at runtime, and pstore support without most persistent backends enabled. Many key storage and filesystem drivers are modules, so boot viability depends on initramfs or early module availability when root/data devices require those drivers.

## Dependencies and Integration Points
- Kernel version dependency: the header says Linux/x86 6.0.9. Later or earlier kernel refs may add, remove, rename, or reinterpret symbols during `oldconfig`/`olddefconfig`.
- Architecture/toolchain dependency: x86_64, GCC-oriented compiler metadata, GNU assembler/linker assumptions, ORC unwinder, x86 virtualization, ACPI/EFI, and x86-specific crypto/debug symbols.
- kdevops dependency: selected by `target_linux_config` defaults such as `config-{{ target_linux_ref }}` and consumed by the `bootlinux` role's clone, copy, configure, build, package, and install tasks.
- Runtime environment dependency: tuned for virtualized guests and lab hosts using virtio, Xen, Hyper-V, KVM, 9p, NVMe, SCSI, CXL, libnvdimm/DAX, RDMA, and debug/tracing workflows.
- Userspace dependency: AppArmor/SELinux/TOMOYO policy loaders, module loading via `/sbin/modprobe`, initramfs contents for modular storage/filesystems, and tooling that reads debugfs, tracefs, proc config, netfilter, or configfs.

## Risks and Edge Cases
- The file is stale by construction for non-6.0.9 kernels. Kconfig reconciliation can silently select defaults for new symbols, drop removed symbols, or alter dependencies; warnings from `oldconfig`/`olddefconfig` are important.
- Boot-critical components are often modular: ext4/XFS/Btrfs/F2FS, SCSI/NVMe/virtio block, 9p FS, and many network/storage transports. A missing initramfs module can make an otherwise successful kernel build unbootable.
- `CONFIG_MODULE_SIG=y` without forced signatures is convenient for labs but can create signing-key churn and does not enforce module authenticity.
- `CONFIG_LSM` lists multiple LSMs, including entries whose specific config is disabled, while AppArmor is the default. Runtime LSM ordering and policy availability should be verified on boot.
- Debug and tracing surfaces increase build size and runtime overhead: `DEBUG_INFO`, ftrace, kmemleak, debugfs, lockup detectors, fault injection, and scheduler stats are useful for research but not representative of lean production kernels.
- Several expected lab filesystems/protocols are disabled: no NFS/NFSD, Ceph, CIFS/SMB, FUSE, or overlayfs. Workflows that expect container overlay storage or network filesystems must add fragments or use a different config.
- Physical hardware coverage is uneven. AHCI, USB storage, many common Intel/Realtek NICs, xHCI, MMC, VFIO, vhost, and virtio-iommu are disabled, so this is safer for VM labs than for arbitrary bare metal.
- Security posture is mixed: hardening features exist, but debugfs, BPF JIT default-on, user namespaces, module force load/unload, and extensive debug/test features expand attack and misuse surfaces in shared environments.

## Test Signals
- Selection signal: run the `bootlinux` config selection path and confirm `linux_config` resolves to `config-v6.0.y` when `target_linux_config=config-v6.0.y`.
- Kconfig reconciliation: in the target Linux checkout, copy this file to `.config` and run `make olddefconfig` or the role's `yes "" | make oldconfig`; inspect stderr/stdout for changed, unknown, or newly defaulted symbols.
- Build signal: complete `make -jN all` or the role's builder/target build path with both the expected GCC path and any LLVM path used by the deployment.
- Boot signal: boot the resulting kernel in the intended guest type and check `uname -r`, `/proc/config.gz`, module loading, initramfs resolution of root/data devices, and serial/console output.
- Storage signal: exercise NVMe, virtio-blk, virtio-scsi, loop/nbd/null_blk, md/dm, XFS/ext4/Btrfs/F2FS, DAX/libnvdimm/CXL paths where expected.
- Virtualization signal: verify KVM guest behavior, virtio net/block/console/balloon, 9p mounts, Xen/Hyper-V modules if those platforms are part of the matrix.
- Debug signal: mount debugfs/tracefs and verify ftrace, kprobe/uprobe events, block I/O tracing, kmemleak controls, and fault-injection controls such as fail_make_request when tests rely on them.
- Negative capability signal: explicitly confirm disabled dependencies for workflows that might assume them, especially NFS, Ceph, overlayfs, FUSE, CIFS, vhost, VFIO, USB storage, xHCI, and AHCI.
