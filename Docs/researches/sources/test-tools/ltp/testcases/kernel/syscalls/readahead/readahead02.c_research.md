# sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c` is a 472-line LTP source file in the `readahead` syscall test area. readahead and POSIX_FADV_WILLNEED coverage for invalid descriptors and page-cache effectiveness on mounted filesystems and overlayfs.

## Important APIs, Types, and Functions

called APIs/macros: `readahead`, `posix_fadvise`, `mincore`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_FILE_LINES_SCANF`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FSYNC`, `SAFE_LSEEK`, `SAFE_LSTAT`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READLINK`, `SAFE_STRTOL`, `SAFE_UMOUNT`, `SAFE_WRITE`; local functions: `libc_readahead`, `fadvise_willneed`, `has_file`, `drop_caches`, `create_testfile`, `read_testfile`, `test_readahead`, `setup_readahead_length`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct stat`, `struct tst_test`, `struct tst_option`, `struct tst_tag`; important macros/constants: `_GNU_SOURCE`, `PROC_IO_FNAME`, `DEFAULT_FILESIZE`, `SHORT_SLEEP_US`, `MIN_RETRY_LIMIT`.

## Control Flow

Function-level flow is organized around `libc_readahead`, `fadvise_willneed`, `has_file`, `drop_caches`, `create_testfile`, `read_testfile`, `test_readahead`, `setup_readahead_length`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is a generated test file, page-cache residency observed with mincore(), /proc/self/io byte counters, optional overlayfs mounts, and the block-device bdi read_ahead_kb sysfs knob. Persistence is limited to temporary files and restored sysfs settings. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `<sys/syscall.h>`, `<sys/mman.h>`, `<sys/mount.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<errno.h>`, `<stdio.h>`, `<stdlib.h>`, `<stdint.h>`, `<unistd.h>`, `<fcntl.h>`, `"config.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_root`, `.mount_device`, `.mntpoint`, `.setup`, `.cleanup`, `.options`, `.test`, `.tcnt`, `.timeout`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

The performance signal depends on cache size, storage speed, overlayfs support, /proc/self/io, mincore accuracy, bdi limits, and drop-caches behavior; the test must report TCONF rather than false failures when the platform cannot expose the signal. Explicit errno expectations include `ENOENT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `readahead on file`; `readahead on overlayfs file`; `read_bytes: %lu`; `readahead calls made: %zu`; `offset is still at 0 as expected`.
