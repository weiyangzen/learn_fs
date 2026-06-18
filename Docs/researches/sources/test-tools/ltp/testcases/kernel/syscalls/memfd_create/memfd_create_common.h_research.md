# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.h

Purpose: change macros accordingly if any flags need to be added in the future

Important APIs/types/functions: fcntl, SAFE_FCNTL, tst_res; local functions detected: none; key constants/macros: MEMFD_TEST_COMMON, FLAGS_ALL_ARRAY_INITIALIZER, FLAGS_ALL_MASK, MFD_DEF_SIZE, GET_MFD_ALL_AVAILABLE_FLAGS, MFD_FLAGS_AVAILABLE, CHECK_MFD_NEW, CHECK_MFD_FAIL_NEW, CHECK_MMAP, CHECK_MMAP_FAIL, CHECK_MUNMAP, CHECK_MFD_HAS_SEALS, CHECK_MFD_ADD_SEALS, CHECK_MFD_FAIL_ADD_SEALS, CHECK_MFD_SIZE, CHECK_MFD_OPEN, CHECK_MFD_FAIL_OPEN, CHECK_MFD_READABLE...

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: preprocessor definitions and declarations only.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
