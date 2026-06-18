# sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c` is a 88-line LTP source file in the `readahead` syscall test area. readahead and POSIX_FADV_WILLNEED coverage for invalid descriptors and page-cache effectiveness on mounted filesystems and overlayfs.

## Important APIs, Types, and Functions

called APIs/macros: `readahead`, `SAFE_CLOSE`, `SAFE_PIPE`, `TST_EXP_FAIL`, `TST_EXP_FAIL_ARR`, `TST_FD_FOREACH`, `TST_TEST_TCONF`; local functions: `test_bad_fd`, `test_invalid_fd`, `test_readahead`, `setup`; struct/table types referenced: `struct tst_fd`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `test_bad_fd`, `test_invalid_fd`, `test_readahead`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is a generated test file, page-cache residency observed with mincore(), /proc/self/io byte counters, optional overlayfs mounts, and the block-device bdi read_ahead_kb sysfs knob. Persistence is limited to temporary files and restored sysfs settings.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/socket.h>`, `<sys/stat.h>`, `<sys/syscall.h>`, `<sys/types.h>`, `"config.h"`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_tmpdir`, `.setup`, `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

The performance signal depends on cache size, storage speed, overlayfs support, /proc/self/io, mincore accuracy, bdi limits, and drop-caches behavior; the test must report TCONF rather than false failures when the platform cannot expose the signal. Explicit errno expectations include `EBADF`, `EINVAL`, `ESPIPE`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `readahead() with fd = -1`; `readahead() with invalid fd`; `readahead() on %s`; `System doesn't support __NR_readahead`.
