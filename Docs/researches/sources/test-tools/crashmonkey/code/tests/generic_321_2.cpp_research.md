# sources/test-tools/crashmonkey/code/tests/generic_321_2.cpp

Purpose: explicit `generic_321_2` rename test. It moves a pre-fsynced root file into a pre-created directory and checks post-crash namespace placement.

Important APIs/types/functions: `Generic321_2`, `open`, `mkdir`, `fsync`, `rename`, `Checkpoint`, directory enumeration, and `DataTestResult`.

Control flow: setup creates `foo` and `test_dir_a`, fsyncs `foo`, syncs, and closes. Run renames `foo` into `test_dir_a/foo`, fsyncs the target directory and moved file, and checkpoints. Check verifies `foo` is absent at root and present under the directory.

State/persistence behavior: both unlink-from-old-parent and link-into-new-parent effects of rename must be durable once the target directory/file are fsynced.

Dependencies/integration: direct syscalls and CrashMonkey checkpointing.

Risks/test signals: parent fsync coverage is asymmetric; root may not be fsynced after rename. The checker treats old-name persistence or missing new name as failure.
