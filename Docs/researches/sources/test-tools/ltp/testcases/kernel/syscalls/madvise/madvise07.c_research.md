# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise07.c

Purpose: Check that accessing a page marked with MADV_HWPOISON results in SIGBUS. Test flow: create child process, map and write to memory, mark memory with MADV_HWPOISON, access memory, if SIGBUS is delivered to child the test passes else it fails If the underlying page type of the memory we have mapped does not support poisoning then the test will fail. We try to map and write to the memory in such a way that by the time madvise is called the virtual memory address points to a supported page. However there may be some rare circumstances where the test produces the wrong result because we have somehow obtained an unsupported page. In such cases ma...

Important APIs/types/functions: mmap, madvise, fork, waitpid, memset, tst_test, tst_res, SAFE_MMAP, SAFE_FORK, SAFE_WAITPID, tst_strstatus; local functions detected: run_child, run; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: run_child, run.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
