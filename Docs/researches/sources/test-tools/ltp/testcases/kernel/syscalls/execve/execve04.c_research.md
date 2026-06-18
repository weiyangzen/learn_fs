# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve04.c

Purpose: Checks historical `ETXTBSY` behavior when trying to execute a file that another process has open for writing.

Important APIs/types/functions: `SAFE_FORK`, LTP checkpoints, `SAFE_OPEN(TEST_APP, O_WRONLY)`, `execve`, `tst_kvercmp`, and `.resource_files`.

Control flow: The child opens the helper for write and waits at a checkpoint. The parent waits until the writer is active, calls `execve`, expects `ETXTBSY`, and then wakes the child.

State and persistence behavior: The helper's open write reference is the key transient state. No durable mutation is intended.

Dependencies and integration points: Uses LTP checkpoint synchronization and skips on kernels 6.11-rc1 and newer where the kernel deliberately changed `i_writecount` behavior.

Risks and test signals: This is version-sensitive by design. On older kernels, wrong success or wrong errno fails; on newer kernels it reports `TCONF`.
