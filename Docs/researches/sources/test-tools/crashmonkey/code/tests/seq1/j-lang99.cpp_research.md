# sources/test-tools/crashmonkey/code/tests/seq1/j-lang99.cpp

Purpose: ACE-generated workload pairing hole punching on `A/foo` with creation and fsync of a separate `A/bar` before checkpoint. It explores whether syncing a sibling file leaves the hole-punch and file creation state vulnerable across simulated crashes.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, `CmClose`, direct `mkdir` and `fallocate`, plus plugin factory exports. It uses the same path inventory as adjacent `j-lang` cases.

Control flow: `run` creates `A`, opens/writes `A/foo`, punches a keep-size hole, creates `A/bar`, fsyncs `A/bar`, checkpoints, optionally stops at checkpoint `1`, and closes both descriptors. `setup` and `check_test` only populate path strings.

State/persistence behavior: logged state includes namespace creation, data write, extent mutation, sibling file creation, fsync, and checkpoint. The intended persistence question is whether fsync on `A/bar` interacts with directory or inode ordering for `A/foo`.

Dependencies/integration: loaded by the C++ harness and evaluated by CrashMonkey diff files. Risks/test signals: no in-test data oracle, direct syscalls bypass the recording wrapper for mkdir/fallocate, and semantics vary by filesystem journaling and delayed allocation behavior.
