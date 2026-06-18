<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/rc -->
# sources/test-tools/blktests/tests/block/rc

Source read: complete file, 11 lines, 161 bytes, sha256 `9937d6056b98b86a`.

Purpose: Block test group prerequisite shim.

Important APIs/types/functions: shell functions `group_requires`. Key helpers/commands referenced include `_have_root`.

Control flow: The group-level `rc` only declares `group_requires` and relies on each numbered test plus common libraries (`null_blk`, `scsi_debug`, `nvme`, `ublk`) to state concrete prerequisites. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/rc -->
