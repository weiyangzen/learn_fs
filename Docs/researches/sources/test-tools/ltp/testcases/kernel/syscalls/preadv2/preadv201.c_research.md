<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c

Purpose: Verify the basic functionality of the preadv2(2): 1. If the file offset argument is not -1, preadv2() should succeed in reading the expected content of data and the file offset is not changed after reading. 2. If the file offset argument is -1, preadv2() should succeed in reading the expected content of data and the current file offset is used and changed after reading.

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`; exercises `preadv2`, `read`; defines `verify_preadv2`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_preadv2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c -->
