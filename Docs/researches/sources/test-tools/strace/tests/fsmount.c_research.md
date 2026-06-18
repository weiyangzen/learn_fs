<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsmount.c -->
# sources/test-tools/strace/tests/fsmount.c

## Purpose
Covers strace decoder coverage for `fsmount`. Source comments describe: Check decoding of fsmount syscall. FSMOUNT_??? FSMOUNT_??? MOUNT_ATTR_??? MOUNT_ATTR_??? Source read: 92 lines, 2621 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <fcntl.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fsmount, main; syscall names/numbers: fsmount, __NR_fsmount; struct types: strval32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is fsmount, __NR_fsmount.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsmount.c -->
