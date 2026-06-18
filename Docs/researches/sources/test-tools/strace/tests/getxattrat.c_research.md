<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat.c -->
# sources/test-tools/strace/tests/getxattrat.c

## Purpose
Covers strace decoder coverage for `getxattrat`. Source comments describe: Check decoding of getxattrat syscall. size < XATTR_ARGS_SIZE_VER0 short read of struct xattr_args size > sizeof(struct xattr_args) XATTR_??? bytes %u..%u size > sizeof(struct xattr_args), short read XATTR_??? size == sizeof(struct xattr_args) AT_??? Source read: 310 lines, 8426 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xmalloc.h", <fcntl.h>, <stdio.h>, <unistd.h>, <linux/xattr.h>, "xlat/xattrat_flags.h"; defines: XLAT_MACROS_ONLY, XATTR_SIZE_MAX, XATTR_ARGS_SIZE_VER0, FD_PATH, YFLAG, SKIP_IF_PROC_IS_UNAVAILABLE; C functions: k_getxattrat, k_setxattrat, main; syscall names/numbers: getxattrat, setxattrat, __NR_getxattrat, __NR_setxattrat; struct types: xattr_args, strival32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is getxattrat, setxattrat, __NR_getxattrat, __NR_setxattrat.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding; temporarily writes an extended attribute on the current directory to make a successful getxattrat value path observable.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat.c -->
