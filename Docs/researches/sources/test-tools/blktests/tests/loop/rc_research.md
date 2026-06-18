<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/rc -->
# sources/test-tools/blktests/tests/loop/rc

Source read: complete file, 20 lines, 361 bytes, sha256 `30c1aee777df11c5`.

Purpose: Loop-device group prerequisite and feature helper file.

Important APIs/types/functions: shell functions `group_requires, _have_loop_set_block_size`. Key helpers/commands referenced include `_have_loop, _have_loop_set_block_size, _have_root, losetup`.

Control flow: It requires root and loop support, and defines `_have_loop_set_block_size` by invoking the local `loblksize` helper on a free loop device. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/rc -->
