# sources/test-tools/crashmonkey/code/tests/seq1/j-lang95.cpp

Purpose: ACE-generated CrashMonkey workload that creates directory `A`, writes 32 KiB of deterministic data to `A/foo`, zeroes a 5,000-byte range near the end with `FALLOC_FL_ZERO_RANGE|FALLOC_FL_KEEP_SIZE`, creates `A/bar`, fsyncs `A/bar`, and records a CrashMonkey checkpoint. It is meant to exercise persistence behavior around sparse/zero-range data operations plus an unrelated synced file in the same directory.

Important APIs/types/functions: `BaseTestCase`, `RecordCmFsOps` through `cm_`, `WriteData`, `fallocate`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, and plugin exports `test_case_get_instance`/`test_case_delete_instance`. The class stores canonical workload paths for root, `A`, `A/C`, `B`, and several file names, although only `A`, `A/foo`, and `A/bar` are active.

Control flow: `setup` initializes paths only. `run` recreates those paths, makes `A`, opens and writes `A/foo`, performs zero-range keep-size fallocate, creates `A/bar`, fsyncs `A/bar`, calls `CmCheckpoint`, optionally exits at checkpoint `1`, then closes both descriptors. `check_test` only resets paths and reports success, so semantic checking is delegated to the CrashMonkey replay/diff harness.

State/persistence behavior: recorded state includes directory creation, file creation, data write, zero-range extent change, fsync of a sibling file, and checkpoint marker. The test intentionally asks whether the checkpoint/replay machinery and target filesystem preserve the state implied by the ordering, not whether this file independently validates bytes.

Dependencies/integration: depends on the crash harness loading the shared object, `BaseTestCase::mnt_dir_`, user-tool wrappers, Linux fallocate flags, and external diff generation. Risks/test signals: no local oracle in `check_test`, direct `mkdir`/`fallocate` calls bypass some wrapper recording, and error paths sometimes close invalid descriptors; failures surface as harness errors or diff artifacts after replay.
