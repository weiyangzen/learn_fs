# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate01.c

Purpose: Legacy LTP basic `fallocate()` functionality test for default mode and `FALLOC_FL_KEEP_SIZE`.

Important APIs/types/functions: `fallocate`, `fstat`, `lseek`, `write`, legacy `test.h`/`tso_safe_macros`, `FALLOC_FL_KEEP_SIZE`, and `lapi/fallocate.h`.

Control flow: `setup()` creates two files, records block size, and writes 12 blocks. Each loop fallocates one block at EOF in default mode expecting file size growth, then with keep-size expecting original size, seeks within the allocated range, and writes one byte.

State and persistence behavior: State is file size, allocated blocks, current file offset, and file contents in a tmpdir.

Dependencies and integration points: Uses old LTP harness and filesystem support detection via `EOPNOTSUPP`/`ENOSYS`.

Risks and test signals: The random write offset is bounded by the allocated length. Failures can indicate unsupported fallocate, incorrect size semantics, broken seek positioning, or unwritable allocated space.
