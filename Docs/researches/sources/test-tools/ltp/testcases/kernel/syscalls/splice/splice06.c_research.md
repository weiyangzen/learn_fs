# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice06.c

## Purpose
This LTP test source exercises `splice` syscall behavior in `splice06.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_path_val`; safe wrappers `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_WRITE`,
`SAFE_WRITE_ALL`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`; harness APIs `tst_test`, `tst_brk`,
`tst_parse_int`, `tst_res`, `tst_path_val`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_tmpdir`. Local functions include `format_str`, `splice_read_num`,
`splice_write_num`, `splice_write_str`, `file_write_num`, `file_write_str`, `file_read_num`,
`splice_test`, `setup`.

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
LTP result macros `TPASS`, `TBROK`, `TCONF`, `TERRNO`.
