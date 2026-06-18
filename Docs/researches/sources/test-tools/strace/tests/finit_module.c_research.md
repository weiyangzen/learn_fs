<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/finit_module.c -->
# sources/test-tools/strace/tests/finit_module.c

## Purpose
Covers strace decoder coverage for `finit_module`. Source comments describe: Check decoding of finit_module syscall. MODULE_INIT_??? Source read: 100 lines, 2683 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "init_delete_module.h"; defines: none; C functions: main; syscall names/numbers: finit_module, __NR_finit_module.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is finit_module, __NR_finit_module.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; touches module-loading syscalls with invalid or synthetic payloads; durable kernel module state is not expected.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; module syscalls may be blocked by privileges, lockdown, or kernel configuration. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/finit_module.c -->
