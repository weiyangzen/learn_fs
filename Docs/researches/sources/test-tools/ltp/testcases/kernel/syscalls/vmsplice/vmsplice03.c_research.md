<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c

Purpose: verifies `vmsplice()` can move data from a pipe into user memory using a read-end pipe descriptor and an output iovec.

Important APIs/types/functions: `setup()` fills a 64 KiB `buffer`. LTP `.bufs` allocates an iovec of the same size. `vmsplice_test()` clears the destination, writes the source buffer into a pipe, calls `vmsplice(pipes[0], iov, 1, 0)`, then compares destination bytes to the source.

Control flow/state: the pipe is created and closed within the test. Successful writes may be partial, but the loop compares up to `TEST_BLOCK_SIZE` and reports pass when all written bytes match.

Dependencies/integration: depends on LTP buffer allocation and `lapi/vmsplice.h`; no tmpdir is needed.

Risks/test signals: partial transfer handling is somewhat loose because the comparison loop iterates over the full block but pass condition uses `i == written`. Failures signal unsupported pipe-to-user transfer or data corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice03.c -->
