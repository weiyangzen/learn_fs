# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice03.c

## Purpose
Verify that, splice(2) returns -1 and sets errno to 1. EBADF if the file descriptor fd_in is not
valid 2. EBADF if the file descriptor fd_out is not valid 3. EBADF if the file descriptor fd_in does
not have proper read-write mode 4. EINVAL if target file is opened in append mode 5. EINVAL if
neither of the descriptors refer to a pipe 6. ESPIPE if off_in is not NULL when the file descriptor
fd_in refers to a pipe 7. ESPIPE if off_out is not NULL when the file descriptor fd_out refers to a
pipe.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tcase`, `struct
tst_test`; safe wrappers `SAFE_FILE_PRINTF`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`,
`SAFE_WRITE_ALL`, `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `setup`, `splice_verify`, `cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EBADF`,
`EINVAL`, `ESPIPE`.
