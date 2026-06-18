# sources/test-tools/crashmonkey/code/tests/generic_321_3.cpp

Purpose: replay-rename subtest from xfstests generic/321. It combines a root-to-directory rename with setting an xattr on the moved file and fsyncing it.

Important APIs/types/functions: `Generic321_3`, `rename`, `fsetxattr`, `fsync`, `Checkpoint`, xattr include selection, `stat`, and `DataTestResult`.

Control flow: setup creates root `foo` and `test_dir_a`, fsyncs the file, and syncs. Run renames `foo` into the directory, fsyncs the directory, sets `user.foo=blah` on the moved file, fsyncs the file, and checkpoints. Check validates namespace placement and usually the moved file's survival.

State/persistence behavior: replay must preserve the rename and the later xattr/inode update without resurrecting the old root name.

Dependencies/integration: requires user xattr support and directory/file fsync behavior.

Risks/test signals: if xattrs are unsupported, the workload fails before reaching its namespace oracle. Signals include missing moved file, old name persistence, and possibly xattr metadata loss depending on check path.
