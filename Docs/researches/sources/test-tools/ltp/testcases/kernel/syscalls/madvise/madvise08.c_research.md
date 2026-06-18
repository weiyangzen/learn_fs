# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise08.c

Purpose: Check that memory marked with MADV_DONTDUMP is not included in a core dump and check that the same memory then marked with MADV_DODUMP is included in a core dump. In order to reliably find the core dump this test temporarily changes the system wide core_pattern setting. Meaning all core dumps will be sent to the test's temporary dir until the setting is restored during cleanup. Test flow: map memory, write generated character sequence to memory, start child process, mark memory with MADV_DONTDUMP in child, abort child, scan child's core dump for character sequence, if the sequence is not found it is a pass otherwise a fail,

Important APIs/types/functions: read, open, close, mmap, munmap, madvise, setrlimit, fork, waitpid, tst_test, SAFE_SETRLIMIT, tst_brk, SAFE_FILE_SCANF, SAFE_GETCWD, tst_res, SAFE_FILE_PRINTF, SAFE_MMAP, SAFE_MUNMAP, SAFE_CLOSE, SAFE_ACCESS, SAFE_OPEN, SAFE_READ, SAFE_FORK, SAFE_WAITPID, tst_path_val, TST_SR_TCONF; local functions detected: setup, cleanup, find_sequence, run_child, run; key constants/macros: CORE_FILTER, YCOUNT, FMEMSIZE, CORENAME_MAX_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, find_sequence, run_child, run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; process resource limits adjusted during setup; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Write a generated character sequence to the mapped memory, which we later look for in the core dump.
