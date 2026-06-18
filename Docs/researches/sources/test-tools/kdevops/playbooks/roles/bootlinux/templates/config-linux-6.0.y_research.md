# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-linux-6.0.y

## Purpose

`sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-linux-6.0.y` is a complete generated Linux kernel `.config` template for an x86_64 Linux 6.0.9 build. It is used by the kdevops `bootlinux` Ansible role as an input configuration for building and installing a test kernel from a selected kernel tree/ref. The file is not executable code; it is a declarative Kconfig state snapshot containing 6,025 lines, with roughly 1,748 enabled/value symbols, 551 module symbols, and 2,657 explicitly disabled symbols.

The practical role of this template is to provide a broad VM- and storage-test-friendly kernel baseline. It enables x86_64, SMP, preemption, namespaces/cgroups, debugfs, tracing, fault injection, block/storage subsystems, common filesystems, 9P, virtio, Xen, Hyper-V, and KVM guest support. Many device and filesystem drivers are modules, keeping the kernel broadly capable while leaving load decisions to the test host and init/runtime environment.

## Integration With `bootlinux`

The role selects the config in `playbooks/roles/bootlinux/tasks/config.yml`. That task builds a `search_list` containing `templates/config-kdevops`, `templates/{{ target_linux_config }}`, and the most recent `config-next-*` fallback, then chooses the first existing file with `with_first_found`. The default `target_linux_config` is `config-{{ target_linux_ref }}` in `defaults/main.yml`, so this file is selected when workflow variables point `target_linux_config` at `config-linux-6.0.y`.

For target-node builds, `tasks/build/targets.yml` copies the selected template to `{{ target_linux_dir_path }}/.config`, optionally writes `localversion`, then runs:

```sh
yes "" | make oldconfig
```

That means this file is a seed, not necessarily the final post-configuration artifact. `make oldconfig` accepts defaults for any symbols not represented in this 6.0-era config when used against a changed kernel tree. The resulting `.config` is then consumed by `{{ target_linux_make_cmd }}`, defaulting to `make -j{{ ansible_processor_vcpus }}`. Separate 9P and builder paths share the same high-level role variables but copy/build from different hosts.

## Important Kconfig Interfaces

The "APIs" in this source are Kconfig symbols that expose kernel subsystems to the rest of the kdevops workflow:

- Boot and build identity: `CONFIG_CC_IS_GCC=y`, GCC 11.3.0, binutils 2.38, `CONFIG_KERNEL_XZ=y`, `CONFIG_BLK_DEV_INITRD=y`, `CONFIG_BOOT_CONFIG=y`, `CONFIG_IKCONFIG=y`, and `CONFIG_IKCONFIG_PROC=y`.
- Architecture and VM target: `CONFIG_64BIT=y`, `CONFIG_X86_64=y`, `CONFIG_SMP=y`, `CONFIG_NR_CPUS=512`, `CONFIG_HYPERVISOR_GUEST=y`, `CONFIG_KVM_GUEST=y`, `CONFIG_XEN=y`, and `CONFIG_PARAVIRT=y`.
- Scheduling and isolation: `CONFIG_PREEMPT=y`, `CONFIG_PREEMPT_DYNAMIC=y`, `CONFIG_NO_HZ_IDLE=y`, `CONFIG_HIGH_RES_TIMERS=y`, `CONFIG_CPU_ISOLATION=y`, cgroups, cpusets, namespaces, and `CONFIG_USER_NS=y`.
- Modules and ABI: `CONFIG_MODULES=y`, forced module load/unload support, `CONFIG_MODVERSIONS=y`, and `CONFIG_MODULE_SIG=y` with SHA-256. `CONFIG_MODULE_SIG_FORCE` is not set, so unsigned modules are not strictly rejected by this config alone.
- Storage/test surface: block layer, blk-mq, null_blk with fault injection, SCSI, virtio-blk, NVMe host/fabrics/target modules, MD RAID, bcache, device mapper targets, target core, RDMA, CXL modules, DAX/NVDIMM, and zoned block support.
- Filesystems: `EXT4_FS=m`, `XFS_FS=m`, `BTRFS_FS=m`, `F2FS_FS=m`, `ZONEFS_FS=m`, `9P_FS=m`, tmpfs, hugetlbfs, quota, fanotify/inotify, fscrypt, and DAX support. Network filesystems such as NFS, NFSD, CIFS, CephFS, and AFS are disabled.
- Virtual I/O: `VIRTIO=m`, `VIRTIO_PCI=m`, `VIRTIO_BLK=m`, `VIRTIO_NET=m`, `VIRTIO_CONSOLE=m`, `VIRTIO_BALLOON=m`, `VIRTIO_MEM=m`, and `NET_9P_VIRTIO=m`. `VHOST_NET` is disabled.
- Observability and fault testing: `CONFIG_DEBUG_FS=y`, `CONFIG_DYNAMIC_DEBUG=y`, `CONFIG_FTRACE=y`, `CONFIG_FUNCTION_TRACER=y`, `CONFIG_KPROBE_EVENTS=y`, `CONFIG_UPROBE_EVENTS=y`, `CONFIG_BPF_EVENTS=y`, `CONFIG_BLK_DEV_IO_TRACE=y`, `CONFIG_DEBUG_KMEMLEAK=y`, `CONFIG_FAULT_INJECTION=y`, `CONFIG_FAIL_MAKE_REQUEST=y`, and `CONFIG_TEST_KMOD=m`.

## Control Flow

This file has no runtime control flow of its own. Its control effect is indirect and happens in the kernel build pipeline:

1. kdevops resolves `linux_config` from the role template search list.
2. The selected template is rendered/copied to the checked-out Linux tree as `.config`.
3. `make oldconfig` reconciles it with the target kernel tree's Kconfig graph, prompting defaults non-interactively through `yes ""`.
4. The kernel build compiles built-in features, modules, and generated metadata according to the reconciled `.config`.
5. Install tasks place the resulting kernel and modules for booting test nodes.

At kernel runtime, control flow is determined by the compiled Linux subsystems. This config biases that runtime toward virtualized x86_64 hosts, dynamic module loading, rich debug/tracing interfaces, and storage/filesystem test coverage.

## State And Persistence

The source file is a persistent repository template. During a bootlinux run it is copied into the mutable kernel checkout as `.config`, then `make oldconfig` may rewrite or supplement that file. Later build products persist under the kernel tree and installed module/kernel paths. The template itself should remain stable unless the intended baseline changes.

Several enabled options expose runtime state:

- `IKCONFIG_PROC` embeds and exposes the running kernel config under `/proc/config.gz`, which is useful for validating that a booted VM actually used this baseline.
- `DEBUG_FS`, ftrace, dynamic debug, fault injection, kmemleak, and tracing options persist runtime control/status through debugfs and tracefs while the kernel is running.
- Module support and module signing affect `/lib/modules/<release>` contents and module-load state.
- Filesystem, block, quota, DAX, pstore, and 9P options determine which persistent storage formats and mounts tests can exercise.

## Dependencies

Build-time dependencies are inherited from the kernel and the bootlinux role: GCC/binutils-compatible toolchain, make, kernel build dependencies installed by `install-deps`, optional ccache, optional Rust dependencies, and enough disk space under `target_linux_dir_path`. The config records GCC/binutils versions from the environment that generated it, but kdevops may build with a different local compiler unless the workflow constrains it.

Runtime dependencies include an x86_64 boot environment, suitable initramfs or root device support, module installation matching the built kernel release, and hypervisor devices matching the enabled drivers. Because many root-relevant drivers are modules, successful boot depends on either an initramfs containing required modules or boot media that only needs built-in support. 9P workflows require the guest to have matching 9P/virtio support and a correct mount tag from the kdevops guestfs path.

## Risks And Edge Cases

- The header says "Automatically generated file; DO NOT EDIT." Manual edits can be overwritten by regeneration and may be hard to audit against Kconfig dependencies.
- The filename `config-linux-6.0.y` is broader than the embedded header `Linux/x86 6.0.9 Kernel Configuration`; applying it to non-6.0 trees relies on `make oldconfig` defaults and may silently enable or disable newer symbols.
- `yes "" | make oldconfig` accepts defaults for new options. That is convenient for automation but can hide security, boot, or subsystem behavior changes during kernel upgrades.
- Several essential devices and filesystems are modules rather than built-ins, including virtio block/network/console, NVMe, SCSI disk, ext4, XFS, Btrfs, F2FS, and 9P FS. Missing initramfs/module installation can turn a successful build into an unbootable or under-featured test node.
- Debug and tracing options increase overhead and kernel attack surface. `DEBUG_FS_ALLOW_ALL`, dynamic debug, ftrace, kmemleak, fault injection, and broad module support are valuable for test labs but are not a hardened production profile.
- Security posture is mixed: SELinux, AppArmor, TOMOYO, Yama, hardening, module signatures, and crypto are enabled, but lockdown, IMA, Landlock, KASAN, KUnit, and forced module signature enforcement are disabled.
- `CONFIG_USB_XHCI_HCD` is disabled, which may surprise users expecting modern USB 3 host support in a generic VM kernel.
- Network filesystem support is intentionally narrow. NFS/NFSD/CIFS/CephFS/FUSE/overlayfs are disabled, which can break workloads or tests that assume those facilities.

## Test Signals

Useful validation signals for this template are:

- The bootlinux Ansible log shows the expected `linux_config` basename and copies it to `{{ target_linux_dir_path }}/.config`.
- `make oldconfig` exits with rc 0 or 141, matching the role's accepted return codes.
- The build completes with `{{ target_linux_make_cmd }}` and module installation produces `/lib/modules/<kernelrelease>`.
- A booted node reports the intended kernel via `uname -r`.
- `/proc/config.gz` exists and contains sentinel options such as `CONFIG_X86_64=y`, `CONFIG_PREEMPT_DYNAMIC=y`, `CONFIG_IKCONFIG_PROC=y`, `CONFIG_DEBUG_FS=y`, `CONFIG_FAULT_INJECTION=y`, `CONFIG_VIRTIO=m`, `CONFIG_9P_FS=m`, `CONFIG_EXT4_FS=m`, and `CONFIG_XFS_FS=m`.
- Storage-oriented tests can load modules such as `null_blk`, `nvme`, `nvmet`, `dm_mod`, `xfs`, `ext4`, `btrfs`, `f2fs`, and `9p`.
- Debug/test workflows can mount debugfs/tracefs and observe ftrace, dynamic debug, fault injection, and kmemleak interfaces.
