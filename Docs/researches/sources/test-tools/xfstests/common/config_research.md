# sources/test-tools/xfstests/common/config

Purpose: core xfstests configuration loader. It sets tool paths, defaults, filesystem-specific mount/mkfs/fsck options, host config section parsing, device validation, overlay overrides, and canonicalization.

Important APIs/flow: exports common environment (`LANG=C`, `HOST`, `CHECK_OPTIONS`, stress factors, debugfs, overlay constants, fsck codes); resolves dozens of program paths (`mkfs`, `mount`, xfs/e2fs/btrfs/f2fs tools, fio, dmsetup, fsverity, etc.); defines `set_mkfs_prog_path_with_opts`, `_common_mount_opts`, `_mount_opts`, `_test_mount_opts`, `_mkfs_opts`, `_fsck_opts`, `_source_specific_fs`, `known_hosts`, `get_config_sections`, `_check_device`, `_canonicalize_mountpoint`, `_canonicalize_devices`, overlay override/restore helpers, `parse_config_section`, and `get_next_config`.

State and persistence: sources host config once or by section; exports `CONFIG_INCLUDED`, `HOST_OPTIONS_SECTIONS`, `OPTIONS_HAVE_SECTIONS`, `FSTYP`, device paths, mount/mkfs/fsck options, and overlay/base variables. It may canonicalize symlink devices and derive `SCRATCH_DEV` from `SCRATCH_DEV_POOL`.

Dependencies and integration: sourced by xfstests `common/rc` and many tests. It depends on Linux, block devices or network fs syntaxes, optional filesystem-specific common files, and many userland tools.

Risks and test signals: this file is central and highly stateful; re-sourcing behavior differs between sectioned and non-sectioned configs. Overlay overrides intentionally mutate `FSTYP`, `TEST_DEV`, `SCRATCH_DEV`, and mount points. Device validation is filesystem-specific. Test signals include running `./check` across sectioned configs, overlay configs, btrfs pools, tmpfs, and missing-tool scenarios.
