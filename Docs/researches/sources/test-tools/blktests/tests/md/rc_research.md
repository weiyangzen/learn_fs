<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/rc -->
# sources/test-tools/blktests/tests/md/rc

Source read: complete file, 459 lines, 15978 bytes, sha256 `c877496caee859bc`.

Purpose: MD/stacked-device shared helper library, especially for atomic-write validation across mdraid, dm, and LVM personalities.

Important APIs/types/functions: shell functions `group_requires, _stacked_atomic_test_requires, _max_pow_of_two_factor, _md_atomics_boundaries_max, _get_vgsize, _md_atomics_test`. Key helpers/commands referenced include `_have_driver, _have_kver, _have_program, _have_root, _have_xfs_io_atomic_write, _md_atomics_boundaries_max, _md_atomics_test, mdadm, vgcreate, lvcreate, lvremove, vgremove, grep, sed`.

Control flow: It requires `mdadm`, probes stacked atomic-write prerequisites, creates md arrays or dm/LVM devices for raid0/raid1/raid10/linear/stripe/mirror, checks sysfs/statx atomic limits, runs atomic `xfs_io` writes, and tears down arrays, superblocks, LVs, and VGs. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/rc -->
