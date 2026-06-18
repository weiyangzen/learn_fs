<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp

## Purpose
This file is a generated CrashMonkey/J-lang `seq1` hard-link metadata crash test. It defines one loadable `BaseTestCase` subclass named `testName` that drives a single checkpoint after a specific filesystem sequence targeting /A/foo -> /bar.

## Important APIs, Types, and Functions
`BaseTestCase`, `setup()`, `run(int checkpoint)`, `check_test(...)`, `test_case_get_instance`, `test_case_delete_instance`, `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, plus POSIX calls used by the variant. The exported C symbols allocate and delete the test object for the dynamic test runner. `setup()` and `run()` both derive canonical paths for the mount root, `/A`, `/B`, `/foo`, `/bar`, and nested variants; only the paths named in this variant are actively mutated.

## Control Flow
`run()` initializes path strings and `local_checkpoint`, performs the variant sequence, executes one persistence barrier, calls `CmCheckpoint()`, returns `1` if the requested checkpoint is reached, then closes remaining descriptors. Variant sequence: creates `/A`, creates `/A/foo`, links it into root as `/bar`, opens `/A`. Barrier: `CmFsync(fd_A)` on the source directory.

## State and Persistence Behavior
The test mutates filesystem namespace and/or file contents under `mnt_dir_`. tests source-directory fsync for a hard link whose destination is the root directory. There is no in-file durable state beyond local descriptors and path strings; crash-state observation is delegated to the CrashMonkey checkpoint/replay framework.

## Dependencies and Integration Points
Depends on CrashMonkey wrapper state from `BaseTestCase::Run`, mount path `mnt_dir_`, `DataTestResult`, `../../user_tools/api/workload.h`, and `../../user_tools/api/actions.h`; raw POSIX calls include `mkdir`, `link`, `fallocate`, `pwrite`, `posix_memalign`, `memcpy`, and mmap/msync helpers through `cm_` depending on the file. The file integrates with the suite through `BaseTestCase::Run` and the `extern "C"` factory/destructor ABI used by CrashMonkey test loading.

## Risks and Edge Cases
The generated `check_test` only rebuilds paths and returns 0, so the recovery oracle is mostly the harness/checkpoint machinery rather than explicit file-content assertions in this file. Error paths often call `CmClose` on possibly invalid descriptors, `posix_memalign` is checked with `< 0` even though it returns positive error codes, and allocated direct-I/O buffers are not freed. Raw metadata syscalls bypass some `CmFsOps` wrappers, which is relevant when reasoning about instrumentation coverage.

## Test Signals
A successful normal run returns 0 after cleanup; a checkpointed run returns 1 immediately after the single `CmCheckpoint()`. Nonzero `errno` or `-1` reports setup, syscall, sync, mmap, or checkpoint failure. The useful signal is whether the crash harness observes a recovered state consistent with the variant's persistence barrier.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang200.cpp -->
