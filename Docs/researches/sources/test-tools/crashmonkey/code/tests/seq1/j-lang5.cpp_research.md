<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests metadata persistence for object creation inside subdirectory `/A`. It performs a compact create/fsync-or-sync sequence and records one checkpoint so the permutation engine can crash after the persistence boundary.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_Afoo` for `/A/foo` regular file, `fd_A` for `/A` directory. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: creates directory `/A` with mode `0777`; opens `/A/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; opens `/A` directory with `O_DIRECTORY` and mode `0777`; fsyncs `/A` directory; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/A/foo` regular file after the checkpoint path; closes `/A` directory after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: directory `/A`, file `/A/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. `CmFsync()` is issued on `/A` directory before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: directory fsync coverage depends on whether the target filesystem records child creation and file extent state through that directory sync; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around namespace/object-creation metadata; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang5.cpp -->
