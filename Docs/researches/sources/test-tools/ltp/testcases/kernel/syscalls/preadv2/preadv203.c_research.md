<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c

Purpose: This is a basic functional test for RWF_NOWAIT flag, we are attempting to force preadv2() either to return a short read or EAGAIN with three concurently running threads: nowait_reader: reads from a random offset from a random file with RWF_NOWAIT flag and expects to get EAGAIN and short read sooner or later writer_thread: rewrites random file in order to keep the underlying device busy so that pages evicted from cache cannot be faulted immediately cache_dropper: attempts to evict pages from a cache in order for reader to hit evicted page sooner or later

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `stdio.h`, `stdlib.h`, `ctype.h`, `pthread.h`, `tst_test.h`, `tst_safe_pthread.h`; exercises `preadv2`, `pwritev`, `read`, `raw syscall path`; defines `drop_caches`, `verify_short_read`, `verify_preadv2`, `check_preadv2_nowait`, `setup`, `do_cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`, `RWF_NOWAIT`.

Control flow centers on `drop_caches`, `verify_short_read`, `verify_preadv2`, `check_preadv2_nowait`, `setup`, `do_cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.min_runtime`, `.needs_root` into the LTP runner. Error-path expectations include `EAGAIN`, `EBADF`, `EOF`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `string.h`, `sys/uio.h`, `stdio.h`, `stdlib.h`, `ctype.h`, `pthread.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_DECLARE_ONCE_FN`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`, `EBADF`, `EOF`, `EOPNOTSUPP`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c -->
