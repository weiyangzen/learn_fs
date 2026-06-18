<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh

## Purpose
This test repeatedly creates, renames, unlinks, and then rereads a surviving file through a mounted export. It targets rename/unlink consistency and directory/getattr visibility after many short file lifecycle operations.

## Important APIs, Types, and Functions
The main variables are `SUB_DIR1=create_rename_unlink-$$`, `FILENAME1`, `FILENAME2`, `NB_ITER_1=100`, `NB_ITER_2=10`, and `ERR`. Commands include `touch`, `mv`, `rm -f`, `ls -li`, and `mkdir -p`.

## Control Flow
For each outer iteration, the script performs 100 repetitions of two sequences: create `FILENAME1`, rename it to `FILENAME2`, unlink it; then create `FILENAME1`, rename to `FILENAME2`, rename back, and unlink. It then creates `FILENAME2`, performs 100 cycles of `ls -li` on the file and directory, removes the file, and repeats. Existence checks before create/rename detect stale names.

## State and Persistence Behavior
State lives in one temporary directory. Unlike several sibling tests, this script does not remove `SUB_DIR1` at the end, so the empty test directory can persist after a successful run. Interrupted runs can also leave files behind.

## Dependencies and Integration Points
It uses Bash-specific syntax under `/bin/sh`. It integrates with NFS-Ganesha by exercising CREATE, RENAME, REMOVE, LOOKUP, GETATTR, and READDIR sequences that are sensitive to directory entry cache invalidation.

## Risks and Test Signals
Risks include missing final cleanup, success exit despite nonzero `ERR`, and reliance on `rm -f` status even when targets are already absent. Test signals are zero reported errors, no unexpected pre-existing filenames, and repeated file/directory listings succeeding after churn.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh -->
