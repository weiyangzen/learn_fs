<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/rc -->
# sources/test-tools/blktests/tests/dm/rc

Source read: complete file, 13 lines, 196 bytes, sha256 `568e03e98a665b23`.

Purpose: Device-mapper test group prerequisites.

Important APIs/types/functions: shell functions `group_requires`. Key helpers/commands referenced include `_have_driver, _have_program, _have_root`.

Control flow: It requires `dmsetup` and the `dm-mod` driver so numbered tests can create linear, dust, and discard/zeroes mapping scenarios. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/dm/rc -->
