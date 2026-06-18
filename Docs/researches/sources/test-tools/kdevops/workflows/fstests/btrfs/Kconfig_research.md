## sources/test-tools/kdevops/workflows/fstests/btrfs/Kconfig

Purpose: Defines the btrfs fstests coverage matrix. It lets distributions choose manual coverage, opt out of RAID56, and select combinations of compression, holes/no-holes, free-space-tree, no-holes plus free-space-tree, simple profile, and ZNS simple-profile sections.

Important APIs/types/functions: This is Kconfig data, so its public surface is config symbols such as `FSTESTS_BTRFS_MANUAL_COVERAGE`, `FSTESTS_BTRFS_ENABLES_COMPRESSION_*`, `FSTESTS_BTRFS_ENABLES_*`, and `FSTESTS_BTRFS_SECTION_*`. Distro capability symbols such as `HAVE_DISTRO_BTRFS_PREFERS_MANUAL` and `HAVE_DISTRO_BTRFS_DISABLES_RAID56` influence defaults.

Control flow: The file branches first on manual coverage. In manual mode, user-visible symbols expose all feature families and section selectors. In non-manual mode, hidden symbols set a default upstream-oriented matrix: compression enabled with zstd, free-space-tree and no-holes/free-space-tree enabled, holes/no-holes legacy sections mostly off, and simple/ZNS sections on.

State and persistence: Kconfig selections persist in `.config` and later become `CONFIG_FSTESTS_BTRFS_*` variables consumed by the fstests Makefile and Ansible extra-vars. No runtime state is written by this file.

Dependencies and integration points: Integrated through the parent `workflows/fstests/Kconfig` when `FSTESTS_BTRFS` is selected. Section names must match fstests config sections and the btrfs Makefile argument names.

Risks and test signals: Risk centers on drift between Kconfig defaults, generated host sections, and btrfs feature support in kernels/progs. Test signals include generated `.config` defaults, `extra_vars.yaml` values produced by Makefiles, and successful provisioning of btrfs sections that match selected symbols.
