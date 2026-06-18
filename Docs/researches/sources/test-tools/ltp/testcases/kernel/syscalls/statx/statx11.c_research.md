<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c

Purpose: It is a basic test for STATX_DIOALIGN mask on block device. - STATX_DIOALIGN Want stx_dio_mem_align and stx_dio_offset_align value These two values are tightly coupled to the kernel's current DIO restrictions on block devices. Minimum Linux version required is v6.1. This test is tightly coupled to the kernel's current DIO restrictions on block devices. The general rule of DIO needing to be aligned to the block device's logical block size was relaxed to allow user buffers (but not file offsets) aligned to the DMA alignment instead. See v6.0 commit bf8d08532bc1 ("iomap: add support for dma aligned direct-io") and they are subject to further change in the future. Also can see commit 2d985f8c6b9 ("vfs: support STATX_DIOALIGN on block devices).

Important APIs/types/functions: includes `sys/types.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `sysfs`, `mount`; defines `verify_statx`, `setup`; uses constants `AT_FDCWD`, `STATX_DIOALIGN`.

Control flow centers on `verify_statx`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_device`, `.needs_root` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/types.h`, `sys/mount.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TST_ASSERT_ULONG`, `TST_EXP_PASS_SILENT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx11.c -->
