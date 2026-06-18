<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_xetattr-common.c -->
# sources/test-tools/strace/tests/file_xetattr-common.c

## Purpose
Covers strace decoder coverage for `file_getattr`. Source comments describe: Check decoding of file_getattr and file_setattr syscalls. size < FILE_ATTR_SIZE_VER0, no read size == FILE_ATTR_SIZE_VER0, no read size == FILE_ATTR_SIZE_VER0, short read size > PAGE_SIZE, no read size > sizeof(struct file_attr), short read size > sizeof(struct file_attr), normal read bytes %u..%u size == sizeof(struct file_attr), normal read Source read: 280 lines, 7457 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xmalloc.h", <fcntl.h>, <stdio.h>, <string.h>, <unistd.h>, <linux/fs.h>, "test_fs_xflags.h"; defines: AT_SYMLINK_NOFOLLOW, AT_EMPTY_PATH, FD_PATH, YFLAG, SKIP_IF_PROC_IS_UNAVAILABLE, RETVAL_INJECTED, INJ_STR; C functions: file_xetattr, main; syscall names/numbers: SYSCALL_NR; struct types: file_attr, strval64, strival32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, Linux UAPI headers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_xetattr-common.c -->
