# sources/test-tools/kdevops/playbooks/roles/bootlinux/templates/config-linux-6.1.y

## Purpose

`config-linux-6.1.y` is a generated Linux kernel `.config` template used by the kdevops `bootlinux` Ansible role when the selected kernel reference resolves to the stable `linux-6.1.y` branch. The role's default `target_linux_config` is `config-{{ target_linux_ref }}`, so a `target_linux_ref` of `linux-6.1.y` maps directly to this template. It gives kdevops a known x86_64 kernel configuration for building and booting test kernels, especially in virtualized environments.

The file is declarative Kconfig state, not executable code. Its important behavior comes from the symbols it enables, disables, or builds as modules, and from how the bootlinux role copies it into a kernel tree as `.config` before running Kconfig normalization and the kernel build.

## Important APIs, types, and symbols

The API surface is the Linux Kconfig symbol set. This file contains 6,081 lines, with approximately 1,652 built-in `=y` symbols, 551 module `=m` symbols, 2,672 explicitly unset symbols, and 111 valued string/integer/hex options.

Important enabled platform and build symbols include `CONFIG_X86_64`, `CONFIG_64BIT`, `CONFIG_SMP`, `CONFIG_NR_CPUS=512`, `CONFIG_PREEMPT`, `CONFIG_PREEMPT_DYNAMIC`, `CONFIG_MODULES`, `CONFIG_MODVERSIONS`, `CONFIG_MODULE_SIG`, `CONFIG_KERNEL_XZ`, `CONFIG_BLK_DEV_INITRD`, and `CONFIG_IKCONFIG_PROC`. Compiler metadata records GCC 11.3.0, GNU binutils assembler/linker, and a generated header for Linux/x86 `6.1.0-rc6`, which is notable because the filename targets the later stable 6.1.y branch.

Virtualization support is broad: Xen guest/dom0 symbols are built in, KVM host modules are enabled through `CONFIG_KVM=m`, `CONFIG_KVM_INTEL=m`, and `CONFIG_KVM_AMD=m`, and virtio devices are generally modular (`CONFIG_VIRTIO=m`, `CONFIG_VIRTIO_PCI=m`, `CONFIG_VIRTIO_BLK=m`, `CONFIG_VIRTIO_NET=m`, `CONFIG_VIRTIO_CONSOLE=m`). Hyper-V, VBox guest, 9p, vsock, paravirtual clocks, and memory balloon/hotplug features are present.

Storage and filesystem coverage is oriented toward test workloads. NVMe, SCSI, device mapper, MD RAID, iSCSI target, zram, loop, null_blk fault injection, and zoned block support are enabled mostly as modules. Filesystems include ext2/3/4, XFS with `CONFIG_XFS_DEBUG=y`, Btrfs, F2FS with fault injection and iostat support, zonefs, FAT/exFAT, ISO9660/UDF, pstore, tmpfs, hugetlbfs, configfs, efivarfs, and 9p. Network filesystems such as NFS, CIFS, CephFS, and AFS are disabled.

Observability and debugging symbols are unusually prominent for a boot test kernel: `CONFIG_DEBUG_KERNEL`, `CONFIG_DEBUG_INFO`, `CONFIG_DEBUG_FS`, `CONFIG_DYNAMIC_DEBUG`, `CONFIG_FTRACE`, `CONFIG_FUNCTION_TRACER`, `CONFIG_FUNCTION_GRAPH_TRACER`, `CONFIG_KPROBES`, `CONFIG_UPROBES`, `CONFIG_BPF_EVENTS`, `CONFIG_BLK_DEV_IO_TRACE`, `CONFIG_DEBUG_KMEMLEAK`, `CONFIG_PAGE_POISONING`, `CONFIG_SCHED_DEBUG`, `CONFIG_SCHEDSTATS`, and multiple lockup/hung-task detectors are enabled. Runtime test modules include `CONFIG_TEST_LKM=m`, `CONFIG_TEST_FIRMWARE=m`, `CONFIG_TEST_SYSCTL=m`, and `CONFIG_TEST_KMOD=m`.

Security and crypto include `CONFIG_SECURITY`, SELinux, AppArmor, TOMOYO, Yama, integrity signature support, module signing, strict kernel/module RWX, hardened usercopy, fortify, seccomp, crypto FIPS mode, many crypto algorithms, and x86 accelerated crypto modules. The default LSM string is broad, while `CONFIG_DEFAULT_SECURITY_APPARMOR=y` selects AppArmor as the default security module.

## Control flow

There is no local control flow inside the template. The execution path is supplied by Ansible and the kernel build system:

1. `roles/bootlinux/tasks/config.yml` builds a search list containing `templates/config-kdevops`, then `templates/{{ target_linux_config }}`, and finally the newest `config-next-*` template if present. It chooses the first existing file with `with_first_found` and stores its basename in `linux_config`.
2. In target-node builds, `tasks/build/targets.yml` clones the requested kernel tree, optionally applies patches, copies `{{ linux_config }}` into `{{ target_linux_dir_path }}/.config`, runs `yes "" | make oldconfig`, and then invokes `{{ target_linux_make_cmd }}`.
3. In builder-node builds, `tasks/build/builder.yml` copies `{{ role_path }}/templates/{{ linux_config }}` to `.config`, then runs `make olddefconfig` for GCC or `make LLVM=1 olddefconfig` for Clang before building.
4. In 9p builds, `tasks/build/9p.yml` has the same basic handoff: copy or merge config into the host tree, normalize with Kconfig, then build.

Because the file is copied as a Jinja template via `ansible.builtin.template`, literal Kconfig lines are rendered unchanged. No variables are embedded in this specific file.

## State and persistence behavior

The persistent state produced by this file is the generated kernel tree's `.config`, plus all downstream build outputs controlled by that `.config`: built-in kernel features, loadable modules, module signatures, debug info, and package/artifact contents. The source file itself is a static checked-in template and should not be edited by the kernel build; the copied `.config` is the mutable build artifact.

Kconfig normalization may rewrite the copied `.config` during `oldconfig` or `olddefconfig`. That means unknown, renamed, removed, or dependency-invalid symbols may be dropped, changed, or supplemented with defaults from the checked-out kernel's Kconfig files. This is expected for a stable branch template but is a risk if the source kernel is not actually compatible with the 6.1-era symbol set.

The template enables `CONFIG_IKCONFIG=y` and `CONFIG_IKCONFIG_PROC=y`, so the running kernel can expose its final config through `/proc/config.gz`. That is an important persistence and verification hook: it allows runtime comparison between this template and the normalized config that actually booted.

## Dependencies

Direct consumers are the `bootlinux` role tasks and the kernel build system. The surrounding playbook dependency chain includes `playbooks/bootlinux.yml`, `roles/bootlinux/defaults/main.yml`, `roles/bootlinux/tasks/config.yml`, and the build-mode-specific task files under `roles/bootlinux/tasks/build/`.

Build-time dependencies are an x86_64-capable Linux kernel source tree, GNU make, a compiler matching the selected mode, binutils or LLVM tools, Kconfig scripts, and module-signing/certificate generation support. Some symbols depend on specific toolchain capabilities captured in the file, such as GCC, assembler, linker, objtool, and stack protector support.

Runtime dependencies depend on the enabled workload. Virtualized boot depends on drivers such as virtio, Xen, Hyper-V, serial console, framebuffer/console support, block/network modules, and 9p when host sharing is used. Storage and filesystem tests depend on loading the relevant modules before use; many test-relevant features are modular rather than built in.

## Integration points

The main integration point is `target_linux_config`, which maps a workflow-selected Linux reference to a template basename. The stable workflow definition lists `linux-6.1.y`, and the bootlinux default converts that to `config-linux-6.1.y`.

The template integrates with the config-fragment path by being bypassed when `bootlinux_use_config_fragments` is true. In that mode, `roles/bootlinux/tasks/config-fragments.yml` starts from kernel defaults and selected fragments instead of copying this full template. Tests or workflows comparing full-template behavior against fragment behavior should account for this split.

The enabled features line up with kdevops-style kernel testing: block layer instrumentation and fault injection, memory hotplug and NUMA, CXL/NVDIMM/DAX support, BPF and tracing, 9p sharing, virtio, KVM/Xen/Hyper-V guests, fs debug options, and module-based storage/network drivers. The template also interacts with update-grub/install tasks later in the role through the kernel image, modules, and package artifacts produced by the build.

## Risks and edge cases

The header says the source was generated for `6.1.0-rc6` while the filename targets `linux-6.1.y`. Stable 6.1.y Kconfig drift can cause `oldconfig`/`olddefconfig` changes, especially for renamed options or new dependencies. The builder path reports Kconfig warnings, but the target-node path using `yes "" | make oldconfig` can silently accept defaults for new prompts.

Many boot-critical drivers are modules, including common virtio block/network paths. This is fine when an initramfs or module installation path is present, but a direct boot without the needed modules in early userspace could fail to find the root disk or network device. The template does enable initrd support, but boot workflows must still package and load modules correctly.

`CONFIG_MODULE_SIG=y` with `CONFIG_MODULE_SIG_KEY=""` relies on kernel build defaults for signing-key generation. Build environments with strict certificate expectations or read-only shared trees can hit signing-key permission or reproducibility issues; the bootlinux tasks include handling for the generated `certs/signing_key.pem`.

The debug-heavy profile increases build time, image/module size, boot memory footprint, and runtime overhead. `CONFIG_DEBUG_INFO=y`, ftrace, kmemleak, page poisoning, XFS debug, lockup detectors, and sched stats are useful for tests but can skew performance-sensitive benchmarks.

Security posture is mixed by design. The file enables many hardening features, but also enables developer/test surfaces such as `CONFIG_DEBUG_FS_ALLOW_ALL`, `CONFIG_DEVMEM`, extensive tracing, module loading/unloading including forced unload, and broad crypto/userspace APIs. That is appropriate for controlled kdevops test nodes, not for a locked-down production baseline.

## Test signals

Static signals: the file should continue to parse as a Linux `.config`, contain the expected `CONFIG_X86_64=y` and `CONFIG_MODULES=y` baseline, and remain reachable through `target_linux_ref=linux-6.1.y` via `target_linux_config=config-linux-6.1.y`.

Build signals: `make olddefconfig` or `yes "" | make oldconfig` should complete without unexpected Kconfig warnings; `make all` should build the image and modules for both GCC and, when requested, Clang. Module signing should produce or reuse `certs/signing_key.pem` without permission failures.

Runtime signals: a booted VM should expose `/proc/config.gz`, load required virtio/Xen/Hyper-V/9p/storage modules, mount the expected root and data filesystems, and provide debugging interfaces such as debugfs, ftrace, BPF events, kprobes, and blktrace where test workflows need them.

Regression signals: compare the normalized `.config` from the build tree or `/proc/config.gz` against this template after kernel updates. Pay attention to removed symbols, changed `=m` versus `=y` decisions for boot-critical drivers, unexpected default selections added by `oldconfig`, and changes in debug/security settings that alter test behavior.
