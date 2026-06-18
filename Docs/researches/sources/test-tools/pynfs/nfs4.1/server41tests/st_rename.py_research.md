# sources/test-tools/pynfs/nfs4.1/server41tests/st_rename.py

Purpose: broad `RENAME` conformance matrix covering successful renames for each object kind, non-directory source/target current filehandles, missing handles, nonexistent names, bad names, replacement type rules, self-renames, hard-link renames, and close-after-overwrite behavior.

Important APIs/types/functions: `testValidDir/File/Link/Block/Char/Fifo/Socket`, `testSfh*`, `testCfh*`, `testNoSfh`, `testNonExistent`, `testZeroLengthOldname`, `testZeroLengthNewname`, `testBadutf8Oldname`, `testBadutf8Newname`, `testDotsOldname`, `testDotsNewname`, `testDirToObj`, `testDirToDir`, `testFileToDir`, `testFileToFile`, `testDirToFullDir`, `testFileToFullDir`, `testSelfRenameDir`, `testSelfRenameFile`, `testLinkRename`, and `testStaleRename`.

Control flow: tests build small directory trees with `maketree` or create special objects with `create_obj`, perform `rename_obj`, and check exact or permitted status sets. Self-rename and hard-link cases inspect `source_cinfo` and `target_cinfo` before/after change attributes to ensure no-op renames do not mutate directory metadata.

State and persistence behavior: creates, moves, replaces, and links objects in the test tree. Replacement tests encode POSIX/NFS ambiguity by accepting alternative statuses such as `EXIST` vs `NOTDIR` or `ISDIR`. `testStaleRename` validates an open target file can still be closed after being overwritten by a rename.

Dependencies/integration: uses environment namespace helpers, invalid UTF-8 corpus, generated `createtype4/specdata4`, and configured test-tree object paths.

Risks and test signals: `testValidChar` creates `NF4BLK` rather than `NF4CHR`, likely reducing char-device-specific coverage. The many accepted status alternatives make the suite tolerant of server differences but less strict. Persistent cleanup relies on environment teardown.
