# sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp

    ## Purpose
    `sources/test-tools/crashmonkey/code/tests/seq1/j-lang118.cpp` is a generated CrashMonkey `seq1` test case. It instantiates the common `testName` subclass of `BaseTestCase` and exercises a single checkpointed sequence in the mounted test filesystem. This specific file is a extent allocation/deallocation crash-consistency workload: creates directory `A_path.c_str()` with mode 0777; opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`; writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes; calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000; fsyncs `fd_Afoo` through the CrashMonkey wrapper; records the single crash checkpoint and may return `1` when the requested checkpoint is reached.

    ## Important APIs, Types, and Functions
    - `fs_testing::tests::testName` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
    - `setup()` and the start of `run()` initialize a fixed path vocabulary rooted at `mnt_dir_`: `A`, `A/C`, `B`, `foo`, `bar`, `A/foo`, `A/bar`, `B/foo`, `B/bar`, `A/C/foo`, and `A/C/bar`.
    - `run(int checkpoint)` uses `CmOpen`, `WriteData`, `fallocate`, `CmFsync`, `CmCheckpoint`, `CmClose`, `mkdir`. The wrapper calls go through `cm_`, which `BaseTestCase::Run` selects as a recording wrapper for checkpoint 0 and a passthrough wrapper for replayed checkpoint executions.
    - `test_case_get_instance()` and `test_case_delete_instance()` are `extern "C"` plugin entry points used by the CrashMonkey test loader.
    - `check_test(...)` currently only rebuilds path strings and returns success, so this file supplies workload generation rather than a rich post-crash oracle.

    ## Control Flow
    The control flow is linear and generated. `setup()` records the canonical path strings and returns 0. `run()` repeats the same path initialization, sets `local_checkpoint` to 0, executes the workload operations below, calls `CmCheckpoint()`, increments `local_checkpoint`, and returns `1` if the caller requested that checkpoint. If the checkpoint does not terminate the run, descriptors are closed and the method returns 0.

    Operation sequence:
    - creates directory `A_path.c_str()` with mode 0777.
- opens `Afoo_path.c_str()` as `fd_Afoo` with flags `O_RDWR|O_CREAT` and mode `0777`.
- writes deterministic data to `fd_Afoo` at offset 0 for 32768 bytes.
- calls `fallocate` on `fd_Afoo` with mode `FALLOC_FL_KEEP_SIZE`, offset 30768, length 5000.
- fsyncs `fd_Afoo` through the CrashMonkey wrapper.
- records the single crash checkpoint and may return `1` when the requested checkpoint is reached.
- closes `fd_Afoo` after the checkpoint path.

    Error handling is immediate: most failed syscalls return `errno`; failed `CmCheckpoint()` returns `-1`. Open/write/allocation failures try to close the affected descriptor before returning.

    ## State and Persistence Behavior
    This test mutates only the mounted filesystem subtree represented by `mnt_dir_`. The relevant persistence boundary is a data file fsync persistence boundary. The single checkpoint after that boundary gives CrashMonkey a crash point for checking whether the filesystem preserves the metadata and/or data implied by the preceding operations. Since `check_test()` does not inspect files, persistence validation is expected to come from the wider CrashMonkey replay/comparison infrastructure or from the operation log serialized when checkpoint 0 uses `RecordCmFsOps`.

    ## Dependencies and Integration Points
    The file includes POSIX headers plus `<attr/xattr.h>`, `../BaseTestCase.h`, and CrashMonkey user-tool helpers from `../../user_tools/api/workload.h` and `../../user_tools/api/actions.h`. In this concrete file, `WriteDataMmap`, `Checkpoint`, xattr APIs, and many predefined path members may be unused generated scaffolding. Integration depends on the dynamic test-loader ABI provided by the `extern "C"` factory/deleter and on `BaseTestCase::init_values` having populated `mnt_dir_` before `setup()` or `run()`.

    ## Risks and Edge Cases
    The largest test-quality risk is the empty oracle: `check_test()` returns 0 without setting `DataTestResult`, so regressions specific to this workload can be missed unless external comparison consumes the serialized workload. The class name `testName` is reused across generated files, so these files must be built as separate test plugins or translation units with isolated symbol loading. Several operations use mode `0777`, depend on `errno` after wrapper failures, and close negative descriptors on open failure, which can make diagnostics noisy. Files involving `fallocate` rely on filesystem support for the selected flags and ranges.

    ## Test Signals
    This 153-line source is itself a test signal for crash-consistency coverage. A successful run should reach one `CmCheckpoint()`, return `1` for the requested checkpoint, and close all opened descriptors when continuing past the checkpoint. Useful validation is to compile it as a CrashMonkey test plugin and run it on filesystems that support the required calls, then confirm the harness receives the expected checkpoint and operation log.
