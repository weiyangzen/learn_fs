<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp

**Purpose**
This CrashMonkey `seq1` generated workload tests crash persistence for a regular-file data/extent update in the mount root. It combines file creation, a deterministic data write when present, and `fallocate` on /foo before a single checkpoint; the allocation variant is `FALLOC_FL_KEEP_SIZE` at offset `30768` for `5000` bytes.

**Important APIs, Types, And Functions**
The local `testName` class derives from `BaseTestCase` and implements `setup()`, `run(int checkpoint)`, and `check_test(unsigned int, DataTestResult *)`; the C ABI factory pair `test_case_get_instance()` / `test_case_delete_instance()` lets the CrashMonkey loader instantiate it. `run()` uses CrashMonkey's `CmFsOps` wrapper for opens, fsyncs, checkpoints, syncs, and closes; opened handles in this file are `fd_foo` for `/foo` regular file. `WriteData` supplies deterministic contents before extent manipulation. The key Linux API under test is `fallocate` with flags `FALLOC_FL_KEEP_SIZE`, offset `30768`, and length `5000`. The source includes `workload.h` and `actions.h`, but only `WriteData` is used when this workload writes file data; `WriteDataMmap` and `Checkpoint` are imported by the generated template but unused here.

**Control Flow**
The flow is linear and has a single checkpoint. `setup()` and the start of `run()` derive all path strings from `mnt_dir_`: `/A`, `/A/C`, `/B`, `/foo`, `/bar`, `/A/foo`, `/A/bar`, `/B/foo`, `/B/bar`, `/A/C/foo`, and `/A/C/bar`. The operation sequence is: opens `/foo` regular file with `O_RDWR|O_CREAT` and mode `0777`; writes 32768 bytes of known data at offset 0 to `/foo` regular file via `WriteData`; calls `fallocate(FALLOC_FL_KEEP_SIZE, 30768, 5000)` on `/foo` regular file; fsyncs `/foo` regular file; records one `CmCheckpoint()` and returns `1` if the harness requested that checkpoint; closes `/foo` regular file after the checkpoint path.

**State And Persistence Behavior**
State is entirely filesystem state under `mnt_dir_`: file `/foo`. The in-memory fields are rebuilt from `mnt_dir_` in `setup()`, `run()`, and `check_test()` and no auxiliary state is persisted by this test. The file data state includes `32768` bytes written at offset `0` to `/foo`. allocates blocks while preserving the visible file size over bytes `30768..35767` (5000 bytes); `FALLOC_FL_KEEP_SIZE` keeps the logical size unchanged. `CmFsync()` is issued on `/foo` regular file before the checkpoint, so the crash image is meant to test what that specific object sync persists. `check_test()` only reinitializes paths and returns success, so this generated case contributes a workload and checkpoint to the CrashMonkey permutation/replay machinery rather than embedding its own oracle.

**Dependencies And Integration Points**
Dependencies are CrashMonkey's dynamic test loading through the exported C factory functions, `BaseTestCase::Run` initialization of `mnt_dir_` and `cm_`, Linux/POSIX filesystem calls from `<fcntl.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<attr/xattr.h>`, and the user-tools wrapper that records disk operations for permutation. The file lives under `tests/seq1`, so it is part of a generated sequence matrix that varies path location, allocation mode, offset, flush target, and sync strength.

**Risks**
Risks and edge cases: filesystem-specific `fallocate` semantics for `FALLOC_FL_KEEP_SIZE` at offset `30768` length `5000`; error cleanup calls `CmClose` even after failed opens, matching the generated style but relying on wrapper tolerance for invalid descriptors.

**Test Signals**
The primary test signal is CrashMonkey's captured disk-write stream around extent allocation/zeroing/sparseness; one checkpoint is emitted after the sync/fsync point, so `checkpoint == 1` stops immediately after that durable-boundary operation. A successful full run returns `0`, syscall or wrapper failures return `errno` (or `-1` for checkpoint failure), and there are no source-local assertions in `check_test()`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang58.cpp -->
