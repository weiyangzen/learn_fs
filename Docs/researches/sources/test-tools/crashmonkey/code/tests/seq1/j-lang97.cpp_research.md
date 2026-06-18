# sources/test-tools/crashmonkey/code/tests/seq1/j-lang97.cpp

Purpose: ACE-generated workload for hole punching under a directory fsync. It creates `A/foo`, writes 32 KiB, punches a keep-size 32 KiB hole starting at byte 32,768, opens directory `A`, fsyncs the directory, and records a checkpoint.

Important APIs/types/functions: `BaseTestCase`, `WriteData`, `CmOpen`, `CmFsync`, `CmCheckpoint`, direct `mkdir` and `fallocate`, and dynamic test-case factory exports. It uses `O_DIRECTORY` to obtain a directory descriptor for `A`.

Control flow: `setup` initializes mount-relative paths. `run` makes `A`, creates/writes `A/foo`, calls `fallocate(FALLOC_FL_PUNCH_HOLE|FALLOC_FL_KEEP_SIZE, 32768, 32768)`, opens `A` as a directory, fsyncs that directory descriptor, checkpoint-exits if requested, then closes file and directory descriptors. `check_test` is a no-op path reset.

State/persistence behavior: the key durable state is a punched sparse range and directory fsync before the checkpoint. The workload targets filesystem behavior where directory fsync may persist namespace metadata but not necessarily file extent contents.

Dependencies/integration: needs Linux hole-punch support and a filesystem that permits directory fsync. Risks/test signals: local validation is absent; direct fallocate is not wrapper-recorded; if directory fsync is unsupported on a target filesystem the workload returns `errno` and is reported as harness failure rather than content mismatch.
