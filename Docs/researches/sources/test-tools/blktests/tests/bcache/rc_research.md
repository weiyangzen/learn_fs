<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/rc -->
# sources/test-tools/blktests/tests/bcache/rc

Source read: complete file, 381 lines, 8400 bytes, sha256 `9d366f7cd4fa0eb2`.

Purpose: Shared bcache test library for creating, registering, removing, wiping, and cleaning bcache devices used by the bcache test group.

Important APIs/types/functions: shell functions `group_requires, _bcache_wipe_devs, _bcache_register, _create_bcache, _remove_bcache, _cleanup_bcache, _setup_bcache`. Key helpers/commands referenced include `_cleanup_bcache, _create_bcache, _have_crypto_algorithm, _have_kernel_options, _have_program, _register_test_cleanup, _remove_bcache, _setup_bcache, dd, blockdev, umount, udevadm, make-bcache, bcache, timeout, cat`.

Control flow: It parses `make-bcache` output for cache-set UUIDs, writes devices to `/sys/fs/bcache/register`, waits for `/dev/bcache/by-uuid` links, stops `/sys/block/bcache*/bcache` devices, unregisters cache sets, and wipes superblock regions before/after tests. Numbered tests source this file before running their `requires`, `device_requires`, `test`, or `test_device` hooks.

State and persistence behavior: The file mutates kernel test devices, sysfs/configfs/debugfs state, temporary files, and test cleanup registrations only while a blktests run is active. Persistent state should be restored by registered cleanup paths and explicit device teardown.

Dependencies and integration points: Integrates with the top-level blktests harness, common shell libraries, root privileges, kernel modules/drivers, udev settlement, and external storage-management tools.

Risks: Cleanup bugs can leave mapped devices, loop/md/dm/bcache state, mounted filesystems, or altered kernel settings behind. Helper assumptions are kernel-version-sensitive and often require destructive test devices.

Test signals: Run the corresponding group with disposable devices and verify skips, cleanup, expected `.out` comparisons, and absence of dmesg warnings or leaked kernel objects after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/bcache/rc -->
