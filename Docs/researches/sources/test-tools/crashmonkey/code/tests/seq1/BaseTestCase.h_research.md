# sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h

## Purpose
`sources/test-tools/crashmonkey/code/tests/seq1/BaseTestCase.h` declares the base interface used by CrashMonkey C++ test plugins. It is an identical copy of the parent `tests/BaseTestCase.h` in this tree, but because it lives under `tests/seq1`, its relative includes point to `tests/results/DataTestResult.h` and `tests/user_tools/api/wrapper.h`, which do not exist at those locations. The generated `seq1/j-lang*.cpp` files include `../BaseTestCase.h`, so they use the parent header rather than this local copy.

## Important APIs, Types, and Functions
- `fs_testing::tests::BaseTestCase` is an abstract base class with virtual `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult*)` hooks.
- `Run(int change_fd, int checkpoint)` is declared as the harness wrapper that chooses the CrashMonkey operation wrapper and invokes `run()`.
- `init_values(std::string mount_dir, long filesys_size)` stores mount and filesystem-size context for derived tests.
- Protected state consists of `mnt_dir_`, `filesys_size_`, and `fs_testing::user_tools::api::CmFsOps *cm_`.
- `test_create_t` and `test_destroy_t` define the C-compatible plugin factory/deleter signatures.

## Control Flow
This header has no implementation, but it defines the lifecycle expected by the harness: create a derived instance, initialize values, call `setup()`, execute `Run(change_fd, checkpoint)`, then call `check_test()` after replay or crash recovery. Derived tests implement only the workload-specific parts; `Run` centralizes wrapper selection and operation serialization in the corresponding `.cpp` implementation.

## State and Persistence Behavior
The header stores mount path and filesystem size but performs no persistence itself. The `cm_` pointer is the critical state handoff: derived tests call `cm_->CmOpen`, `cm_->CmFsync`, `cm_->CmCheckpoint`, and related wrappers so the harness can record or replay filesystem operations. If `init_values` is skipped, generated tests will build paths from an empty `mnt_dir_`.

## Dependencies and Integration Points
It depends on `DataTestResult` for post-crash outcome reporting and `CmFsOps` from the user-tools wrapper API for syscall mediation. The ABI is designed for dynamically loaded tests exposing `test_case_get_instance` and `test_case_delete_instance`. As a `seq1` copy, this file is a risky integration artifact: direct inclusion from the `seq1` directory would resolve relative includes differently from the parent copy and currently appears broken unless matching `seq1/results` and `seq1/user_tools` trees are supplied.

## Risks and Edge Cases
The destructor is virtual, which is correct for plugin deletion through the base pointer. The raw `cm_` pointer is non-owning and valid only during `Run`; derived code should not retain it beyond the call. The duplicated header can drift from the parent header or accidentally be included by new `seq1` files, causing build failures due to bad relative include paths.

## Test Signals
The main verification signal is compile/link behavior of CrashMonkey test plugins and successful dynamic loading through the factory typedefs. A focused guard should compare this file with the parent `tests/BaseTestCase.h` and either keep them intentionally synchronized or remove/avoid the duplicate include path.
