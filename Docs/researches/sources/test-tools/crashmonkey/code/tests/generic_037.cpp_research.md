# sources/test-tools/crashmonkey/code/tests/generic_037.cpp

Purpose: xattr persistence workload based on xfstests generic/037. It verifies that an extended attribute set on a file remains available with the expected value after crash recovery and checkpointed fsync.

Important APIs/types/functions: `Generic037`, xattr headers selected by `NEW_XATTR_INC`, `fsetxattr`/`getxattr`, `open`, `fsync`, `Checkpoint`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: setup creates `foo` and syncs. The run path sets an xattr value, fsyncs the file, checkpoints, and returns. The checker reads the attribute and compares it against the expected `val1` value.

State/persistence behavior: attribute name/value metadata is the durable state under test. The file itself is pre-created, so the interesting persistence boundary is xattr logging during file fsync.

Dependencies/integration: depends on user xattr support and either `<sys/xattr.h>` or `<attr/xattr.h>`.

Risks/test signals: the workload can be skipped or fail on filesystems/mounts without user xattrs. Signal is missing or mismatched recovered xattr.
