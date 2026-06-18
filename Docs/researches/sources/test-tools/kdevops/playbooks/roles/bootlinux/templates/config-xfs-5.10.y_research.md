# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-5.10.y

## Purpose

`config-xfs-5.10.y` is a generated Linux/x86 kernel `.config` template for kdevops `bootlinux` builds targeting Linux 5.10.105. It is byte-identical to the role's `config-v5.10.105` template, but its name advertises an XFS-oriented 5.10.y baseline that can be selected through `target_linux_config=config-xfs-5.10.y`.

The file is not procedural code; it is declarative Kconfig state consumed by the Linux kernel build. Its primary value is reproducibility: it fixes a known x86_64 guest-capable kernel feature set with XFS built as a module, XFS quota/ACL/realtime/debug support enabled, and a large set of storage, virtualization, tracing, and fault-injection options useful for filesystem development.

## Important APIs, Types, and Configuration Surfaces

There are no functions or language-level types in this file. The effective API is the set of `CONFIG_*` symbols exported to Kbuild, generated headers, built-in code, and module build decisions.

Important XFS and filesystem symbols:

- `CONFIG_XFS_FS=m`: builds XFS as a loadable module, so tests must ensure module installation and loading are working.
- `CONFIG_XFS_SUPPORT_V4=y`: keeps support for older V4 XFS on-disk formats.
- `CONFIG_XFS_QUOTA=y`: enables XFS quota support.
- `CONFIG_XFS_POSIX_ACL=y`: enables POSIX ACL behavior for XFS.
- `CONFIG_XFS_RT=y`: enables XFS realtime subvolume support.
- `CONFIG_XFS_DEBUG=y`: enables XFS debug checks and diagnostics.
- `# CONFIG_XFS_ONLINE_SCRUB is not set`: excludes online scrub infrastructure for this 5.10.y baseline.
- `# CONFIG_XFS_ASSERT_FATAL is not set`: XFS assertions are debug-enabled but not configured to be fatal.
- `CONFIG_FS_IOMAP=y`, `CONFIG_FS_DAX=y`, `CONFIG_FS_DAX_PMD=y`: exposes iomap and DAX paths relevant to XFS coverage.
- `CONFIG_QUOTA=y`, `CONFIG_QUOTACTL=y`, `CONFIG_FS_POSIX_ACL=y`: global filesystem quota and ACL plumbing needed by XFS features.

Important storage and device symbols:

- `CONFIG_BLOCK=y`, `CONFIG_BLK_MQ_PCI=y`, `CONFIG_BLK_MQ_VIRTIO=y`, `CONFIG_BLK_DEBUG_FS=y`, `CONFIG_BLK_DEV_IO_TRACE=y`: enables modern block infrastructure and observability.
- `CONFIG_VIRTIO_BLK=m`, `CONFIG_VIRTIO_PCI=m`, `CONFIG_SCSI_VIRTIO=m`: supports common kdevops/QEMU block devices as modules.
- `CONFIG_NVME_CORE=m`, `CONFIG_BLK_DEV_NVME=m`, `CONFIG_NVME_MULTIPATH=y`: supports NVMe test disks as modules.
- `CONFIG_SCSI=m`, `CONFIG_BLK_DEV_SD=m`, `CONFIG_SCSI_DEBUG=m`: supports SCSI disks and synthetic SCSI debugging devices.
- `CONFIG_BLK_DEV_DM=m`, `CONFIG_DM_THIN_PROVISIONING=m`, `CONFIG_DM_FLAKEY=m`, `CONFIG_DM_LOG_WRITES=m`, `CONFIG_DM_DELAY=m`: enables device-mapper scenarios frequently used in filesystem failure and replay tests.

Important virtualization and boot symbols:

- `CONFIG_64BIT=y`, `CONFIG_X86_64=y`: constrains the template to x86_64.
- `CONFIG_HYPERVISOR_GUEST=y`, `CONFIG_KVM_GUEST=y`, `CONFIG_XEN=y`, `CONFIG_PARAVIRT=y`: makes the kernel suitable for guest execution.
- `CONFIG_MODULES=y`, `CONFIG_MODULE_UNLOAD=y`, `CONFIG_MODVERSIONS=y`, `CONFIG_MODULE_SIG=y`: uses a modular kernel with signed module infrastructure.
- `CONFIG_BLK_DEV_INITRD=y`, `CONFIG_DEVTMPFS=y`, `CONFIG_TMPFS=y`, `CONFIG_PROC_FS=y`, `CONFIG_SYSFS=y`: supports normal distro-style boot and runtime device discovery.
- `CONFIG_NET_9P=y`, `CONFIG_9P_FS=m`, `CONFIG_NET_9P_VIRTIO=m`: supports 9p host/guest sharing used by some kdevops bootlinux modes.

Important debug and test symbols:

- `CONFIG_DEBUG_INFO=y`, `CONFIG_DEBUG_FS=y`, `CONFIG_DYNAMIC_DEBUG=y`, `CONFIG_MAGIC_SYSRQ=y`: improves post-failure diagnosis.
- `CONFIG_FTRACE=y`, `CONFIG_FUNCTION_TRACER=y`, `CONFIG_FUNCTION_GRAPH_TRACER=y`, `CONFIG_KPROBES=y`, `CONFIG_UPROBES=y`, `CONFIG_BPF_EVENTS=y`: supports tracing and dynamic probes.
- `CONFIG_FAULT_INJECTION=y`, `CONFIG_FAIL_MAKE_REQUEST=y`, `CONFIG_FAIL_FUNCTION=y`, `CONFIG_FAULT_INJECTION_DEBUG_FS=y`: enables targeted failure-injection tests.
- `CONFIG_LOCKUP_DETECTOR=y`, `CONFIG_DETECT_HUNG_TASK=y`, `CONFIG_SCHED_DEBUG=y`, `CONFIG_DEBUG_LIST=y`, `CONFIG_BUG_ON_DATA_CORRUPTION=y`: surfaces hangs and data-structure misuse.
- `# CONFIG_KUNIT is not set`, `# CONFIG_KASAN is not set`, `# CONFIG_KCSAN is not set`, `# CONFIG_KCOV is not set`: this is a debug-friendly but not sanitizer- or unit-test-heavy config.

## Control Flow and Selection Path

The template is selected by kdevops through the `bootlinux` role rather than by code inside the file. `playbooks/roles/bootlinux/defaults/main.yml` defines `target_linux_config` as `config-{{ target_linux_ref }}` by default. Users or workflow generators can override this to `config-xfs-5.10.y`.

`playbooks/roles/bootlinux/tasks/config.yml` builds a search list containing:

- `{{ role_path }}/templates/config-kdevops`
- `{{ role_path }}/templates/{{ target_linux_config }}`
- the newest `config-next-*` template, when present

The task then uses Ansible `with_first_found` to set `linux_config` to the first available basename. When this file is the requested template, it becomes the base `.config` for the kernel tree. If `bootlinux_use_config_fragments` is enabled, `tasks/config-fragments.yml` can subsequently run Linux `scripts/kconfig/merge_config.sh -n .config ...` to merge upstream or kdevops fragments, meaning the final build config can differ from this template.

In the kernel build itself, Kbuild reads `.config`, emits generated configuration headers, and builds features as built-in (`y`), module (`m`), or absent based on these symbols. The control flow affected by this file is therefore compile-time and module-load-time behavior rather than runtime branching in the template.

## State and Persistence Behavior

The source file is persistent repository state: a checked-in generated Kconfig snapshot. It contains no mutable runtime state. During a bootlinux run, its contents are copied or applied into the target kernel source as `.config`; later tasks can run `make olddefconfig`, compile modules and the kernel, install modules, and update the bootloader.

Several configured subsystems affect runtime persistence and test state:

- XFS itself is a persistent filesystem module and can create or mount durable on-disk metadata.
- `CONFIG_XFS_SUPPORT_V4=y` preserves compatibility with legacy XFS metadata layouts.
- Quota configuration enables persistent quota accounting paths when filesystems are mounted with quota options.
- `CONFIG_PSTORE=y` is enabled, but RAM pstore backends are not enabled, so crash persistence depends on platform/backend availability.
- `CONFIG_IKCONFIG=m` embeds kernel config access as a module, while `# CONFIG_IKCONFIG_PROC is not set` means `/proc/config.gz` is not exposed by default.
- Module-heavy storage support means runtime availability depends on modules being installed and discoverable in the booted kernel's module directory.

## Dependencies

Build-time dependencies include a Linux 5.10.y-compatible Kconfig tree, Kbuild, and a compiler environment matching the selected architecture. The header records GCC 11.2.0 and binutils ld 2.38 as the generation environment, but the file can be consumed by compatible toolchains when Kconfig symbols remain valid.

Ansible integration dependencies include:

- the kdevops `bootlinux` role and its `target_linux_config` variable;
- `community.general.version_sort` when discovering newest `config-next-*` templates;
- optional `scripts/kconfig/merge_config.sh` in the Linux source tree if fragments are enabled;
- module installation and initramfs/bootloader handling for modular block, virtio, NVMe, SCSI, XFS, ext4, btrfs, 9p, and network features.

Runtime dependencies for representative XFS tests include:

- userspace XFS tools such as `mkfs.xfs`, `xfs_repair`, and xfstests helpers;
- block devices backed by virtio, NVMe, SCSI, device-mapper, or loop modules;
- debugfs mounted for tracing, block debug, and fault-injection controls;
- a kernel/module install path that matches the booted kernel release, especially because XFS is not built in.

## Integration Points

The main integration point is `playbooks/roles/bootlinux/tasks/config.yml`, which resolves this template by basename from `target_linux_config`. `defaults/main.yml` documents the variable and sets the default pattern, while the role README describes `target_linux_ref` and `target_linux_config` as user-facing bootlinux inputs.

The file also integrates indirectly with:

- `tasks/config-fragments.yml`, which can merge additional fragments after the base config is selected;
- `tasks/build/*.yml`, which compile and install the selected kernel and modules;
- kdevops workflows that set `data_fstype: xfs` and attach QEMU/NVMe-style data devices;
- xfstests or other filesystem workflows that expect XFS quota, ACL, realtime, DAX/iomap, tracing, and failure-injection support;
- QEMU/KVM/Xen environments through paravirtual, virtio, serial console, and 9p settings.

Because the file is identical to `config-v5.10.105`, any maintenance change made to one should be evaluated for the other. If they intentionally remain aliases, drift between the two files would be a signal that one path is stale.

## Risks and Edge Cases

- XFS is modular. Booting or testing root-on-XFS, early mount paths, or minimal initramfs environments can fail if `xfs.ko` or its dependencies are not included.
- `CONFIG_XFS_ONLINE_SCRUB` is disabled. Tests requiring `xfs_scrub` online kernel support or online repair coverage cannot use this template without fragment or template changes.
- `CONFIG_XFS_DEBUG=y` changes runtime checking and performance characteristics. It is valuable for development, but results may differ from production-style kernels.
- `CONFIG_XFS_ASSERT_FATAL` is disabled. Some debug assertions may warn or continue rather than immediately panic, which affects failure signal semantics.
- Module signing is enabled, but `CONFIG_MODULE_SIG_KEY=""` and force-signing is not enabled. Build/install flows need to handle generated signing keys consistently if signatures matter.
- Several storage drivers are modules, including virtio block, NVMe, SCSI disk, device mapper, and XFS. Missing initramfs generation or module installation can look like device or filesystem regressions.
- The file is architecture-specific to x86_64 and not suitable for ARM64 or other platforms without reconfiguration.
- The generated header says "DO NOT EDIT"; manual edits can be overwritten by `make olddefconfig`, fragment merging, or regeneration.
- Sanitizers and deeper kernel test frameworks are disabled (`KASAN`, `KCSAN`, `KUNIT`, `KCOV`), so memory/concurrency bugs may need another config.
- Online filesystem encryption and verity are disabled, so tests for encrypted or verity-enabled filesystem behavior are out of scope.

## Test Signals

Useful validation signals for this template are:

- `cmp sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-xfs-5.10.y sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-v5.10.105` remains clean if the alias relationship is intended.
- A bootlinux run with `target_linux_config=config-xfs-5.10.y` selects this basename in the Ansible `linux_config` fact.
- `make olddefconfig` against the intended Linux 5.10.y tree completes without unexpected symbol churn.
- The built kernel boots on the intended kdevops x86_64 guest target and can load `xfs`, `virtio_blk` or `nvme`, `dm_mod`, and any required storage modules.
- `zgrep` or `/boot/config-*` on the installed kernel reports `CONFIG_XFS_FS=m`, `CONFIG_XFS_QUOTA=y`, `CONFIG_XFS_POSIX_ACL=y`, `CONFIG_XFS_RT=y`, `CONFIG_XFS_DEBUG=y`, and no `CONFIG_XFS_ONLINE_SCRUB`.
- Smoke tests can create, mount, unmount, and repair an XFS filesystem on the kdevops data device.
- Quota and ACL tests observe kernel support rather than "operation not supported" failures.
- Fault-injection and tracing tests can mount debugfs and access block failure injection, ftrace, kprobes, dynamic debug, and block I/O tracing controls.
- Negative test signal: online scrub tests should be skipped or expected to report missing kernel support unless another fragment enables that feature.
