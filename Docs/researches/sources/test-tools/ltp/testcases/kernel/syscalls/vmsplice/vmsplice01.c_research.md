<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c

Purpose: positive data-integrity test for splicing a 128 KiB user buffer into a pipe with `vmsplice()`, then from pipe to file with `splice()`, and reading the file back.

Important APIs/types/functions: `setup()` fills `buffer` with byte pattern. `vmsplice_test()` opens `vmsplice_test_file`, creates a pipe, polls for writable space, repeatedly calls `vmsplice()` on a moving `iovec`, and `SAFE_SPLICE()`s written bytes to the file. `check_file()` reads back the full block and compares byte-by-byte.

Control flow/state: the iovec advances until all bytes are moved or `vmsplice()` returns zero. Persistent state is one temporary file containing the spliced buffer.

Dependencies/integration: depends on `lapi/splice.h`, `lapi/vmsplice.h`, poll, pipes, and LTP tmpdir. NFS is skipped because splice/file semantics may differ.

Risks/test signals: partial writes are expected and handled; data mismatch identifies pipe/splice corruption. A hang would imply poll/write progress issues, while syscall errors are `TBROK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice01.c -->
