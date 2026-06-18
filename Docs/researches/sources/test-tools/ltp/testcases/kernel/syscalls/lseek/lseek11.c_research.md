# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek11.c

Purpose: This case create 3 holes and 4 data fields, every (data) is 12 bytes, every UNIT has UNIT_BLOCKS * block_size bytes. The structure as below: ---------------------------------------------------------------------------------------------- data01suffix (hole) data02suffix (hole) data03suffix (hole) data04sufix ---------------------------------------------------------------------------------------------- |<--- UNIT_BLOCKS blocks --->||<--- UNIT_BLOCKS blocks --->||<--- UNIT_BLOCKS blocks --->|

Important APIs/types/functions: lseek, write, read, open, close, ftruncate, memset, fstat, fsync, pwrite, tst_test, tst_safe_prw, SAFE_CLOSE, SAFE_FSTAT, SAFE_FTRUNCATE, SAFE_PWRITE, SAFE_FSYNC, tst_brk, SAFE_LSEEK, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_OPEN, tst_res, SAFE_READ; local functions detected: cleanup, get_blocksize, write_data, setup, test_lseek; key constants/macros: UNIT_COUNT, UNIT_BLOCKS, FILE_BLOCKS

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, get_blocksize, write_data, setup, test_lseek.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: SEEK from "startblock * block_size - offset", "whence" as the directive whence. startblock * block_size - offset: as offset of lseek() whence: as whence of lseek() data: as the expected result read from file offset. NULL means expect the end of file. count: as the count read from file SEEK_DATA from starting of file
