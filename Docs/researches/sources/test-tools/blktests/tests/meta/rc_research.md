<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->
# sources/test-tools/blktests/tests/meta/rc

Source read: complete file, 64 lines, 2230 bytes, sha256 `e080e5e7ee04d6d7`.

Purpose: Self-test helper file for the blktests runner's metadata, skip, dmesg, and condition-combination behavior.

Important APIs/types/functions: shell functions `group_requires, group_device_requires, fake_bug_on`. Key helpers/commands referenced include `cat`.

Control flow: It defines group and device requirements, writes synthetic dmesg content, and supplies hooks used by numbered meta tests to validate runner filtering, `TEST_RUN` metadata capture, and `_set_combined_conditions` expansion. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->
