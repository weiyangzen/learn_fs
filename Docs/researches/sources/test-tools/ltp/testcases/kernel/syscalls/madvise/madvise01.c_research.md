# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise01.c

Purpose: This is a test case for madvise(2) system call. It tests madvise(2) with combinations of advice values. No error should be returned.

Important APIs/types/functions: write, open, close, mmap, munmap, madvise, mkdir, mount, umount, fstat, tst_test, SAFE_MKDIR, SAFE_MOUNT, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_FSTAT, SAFE_MMAP, SAFE_CLOSE, SAFE_MUNMAP, SAFE_UMOUNT, TST_RET, TST_ERR, tst_res, tst_strerrno; local functions detected: setup, cleanup, verify_madvise; key constants/macros: TMP_DIR, TEST_FILE, STR

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, verify_madvise.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Writing 40 KB of random data into this file [32 * 1280 = 40960] Map the input file into shared memory
