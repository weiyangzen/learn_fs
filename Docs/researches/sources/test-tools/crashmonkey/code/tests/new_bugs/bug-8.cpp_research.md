# sources/test-tools/crashmonkey/code/tests/new_bugs/bug-8.cpp

Purpose: generated keep-size fallocate workload. It writes 4 KiB to root `foo`, allocates another 4 KiB beyond EOF with `FALLOC_FL_KEEP_SIZE`, fsyncs, and checkpoints.

Important APIs/types/functions: `testName`, `cm_->CmOpen`, `WriteData`, `fallocate(FALLOC_FL_KEEP_SIZE)`, `cm_->CmFsync`, `cm_->CmCheckpoint`, `stat`, and `DataTestResult`.

Control flow: run opens/creates `foo`, writes 4096 bytes at offset 0, keep-size fallocates 4096 bytes at offset 4096, fsyncs `foo`, checkpoints, and returns. Setup/check only initialize and validate path state.

State/persistence behavior: logical file size should remain 4 KiB while allocation metadata may include the next block. It is a compact version of EOF allocation persistence checks.

Dependencies/integration: Linux fallocate support and `cm_` wrappers for open/fsync/checkpoint.

Risks/test signals: checker details determine whether it validates size, block count, or only file presence. Main expected risks are incorrect size growth or lost allocation metadata.
