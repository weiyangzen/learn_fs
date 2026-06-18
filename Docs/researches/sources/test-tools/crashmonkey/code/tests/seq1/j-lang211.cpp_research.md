# sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp

Source path: `sources/test-tools/crashmonkey/code/tests/seq1/j-lang211.cpp`
Work item: `subset-b-009212`

## Purpose
This generated CrashMonkey seq1 test implements a `BaseTestCase` plugin that exercises cross-directory hard link from root file /bar into A/bar, with the destination directory A fsynced. It is a one-checkpoint crash workload: the test performs a small sequence of filesystem calls under `mnt_dir_`, applies `fsync directory A` as the durability stimulus, records `CmCheckpoint()`, and returns `1` when the harness asks to stop at that checkpoint.

## Important APIs, Types, and Functions
- `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`.
- The CrashMonkey wrapper `cm_` is used for `CmOpen`, `CmClose`, `CmFsync`, `CmSync`, `CmCheckpoint`, and, for rename cases, `CmRename`; direct POSIX or libc calls provide `mkdir`, `link`, `unlink`, `remove`, `fallocate`, and file mode flags.
- `WriteData` is relevant for fallocate workloads; `WriteDataMmap`, `Checkpoint`, `TEST_FILE_PERMS`, and the `<attr/xattr.h>` include are present boilerplate but unused in this file.
- The `extern "C"` factory and delete functions expose the test to the CrashMonkey dynamic test loader.

## Control Flow
`setup()` and the start of `run()` derive the same path set from `mnt_dir_`: the mount root, `A`, `A/C`, `B`, root files `foo` and `bar`, and nested variants under `A`, `B`, and `A/C`. `run()` initializes `local_checkpoint` to zero, then executes this file-specific sequence: mkdir A; create /bar; hard-link /bar to A/bar; open A as directory; CmFsync(A); checkpoint. After `CmCheckpoint()` succeeds, it increments `local_checkpoint`, returns `1` if the caller requested checkpoint 1, otherwise closes any remaining open descriptors and returns `0`. `check_test()` only rebuilds the path strings and returns success without inspecting `test_result`.

## State and Persistence Behavior
All durable state is external filesystem state under the mounted test directory; in-memory state is limited to path strings, local descriptors, and `local_checkpoint`. The workload focuses on namespace link-count update through POSIX link(). The selected flush action is `fsync directory A`, so the test probes whether that flush is sufficient for the preceding namespace or data change. If the harness crashes at checkpoint 1, descriptor cleanup after the checkpoint may not run; that is intentional because the crash point is between the persistence operation and later cleanup.

## Dependencies and Integration Points
The file depends on Linux filesystem headers and CrashMonkey's `BaseTestCase`, `workload.h`, and `actions.h`. It integrates with the CrashMonkey/user-tools API through `cm_`, which records wrapped operations and establishes the crash checkpoint. The direct system calls are important because they bypass some wrapper semantics while still operating inside the mounted test filesystem.

## Risks and Edge Cases
The largest research risk is that `check_test()` contains no explicit oracle, so correctness depends on an external CrashMonkey checker or comparison harness rather than assertions in this file. Error handling returns `errno` or `-1`, but some wrapper failures may not set `errno` reliably. Several error branches call `CmClose()` on negative descriptors, matching surrounding generated code but potentially obscuring the primary failure. The broad path boilerplate also declares directories and files unused by this specific sequence, which can make manual review noisy.

## Test Signals
A useful run reaches `CmCheckpoint()` and returns `1` for checkpoint 1. Failures before the checkpoint return a nonzero `errno`, while checkpoint failure returns `-1`. The post-crash namespace should reveal whether both directory entries name the same inode and whether link-count metadata survived the selected flush boundary. The absence of explicit `DataTestResult` checks means this file is best interpreted as a workload generator whose signal is consumed by the larger crash-recovery framework.
