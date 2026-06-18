# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_badblocks.c

Standalone test program for the libext2fs badblocks list implementation. It builds several test vectors, checks sorted/duplicate behavior, validates membership queries, performs add/delete sequences, compares lists, and tests file serialization/deserialization.

`file_test` writes a badblocks list to a temporary file and reads it back with `ext2fs_read_bb_FILE2`. `file_test_invalid` creates a minimal fake filesystem, appends an invalid block number to the serialized file, verifies the invalid-block callback fires, and confirms the resulting list still matches the valid input.

The program reports failures through `test_fail` and returns that count as its exit status.
