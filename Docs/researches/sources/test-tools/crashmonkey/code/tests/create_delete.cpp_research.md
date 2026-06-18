# sources/test-tools/crashmonkey/code/tests/create_delete.cpp

Purpose: creates multiple randomly-filled files in a subdirectory, checkpoints after each create/write, then deletes them with checkpoints after each removal. It is a general crash-consistency oracle for create, fsync, writeback, delete, and cleanup ordering.

Important APIs/types/functions: `create_delete`, `Checkpoint`, `/dev/urandom` reads, `mkdir`, `open`, `write`, `fsync`, `sync`, `remove`, `stat`, and `DataTestResult`. The class stores generated text in a member buffer used by `check_test()`.

Control flow: `setup()` creates and fsyncs the test directory and fills an in-memory random buffer. `run()` creates a fixed sequence of files, fsyncs the new inode, writes the buffer, fsyncs again, and checkpoints. It then removes the same files, calls global `sync()`, and checkpoints after each delete.

State/persistence behavior: before delete checkpoints, each expected file must have the correct regular-file metadata, size, and exact byte contents. After delete checkpoints, old files should no longer remain.

Dependencies/integration: depends on the CrashMonkey snapshot mount and POSIX namespace/data operations; no `cm_` wrapper is used for the main syscalls, so it is closer to a direct workload.

Risks/test signals: random data makes oracle state process-local; rerunning `check_test()` without the same object state would be invalid. Failure modes include missing expected files, corrupt size/mode/data, or old files persisting after deletion.
