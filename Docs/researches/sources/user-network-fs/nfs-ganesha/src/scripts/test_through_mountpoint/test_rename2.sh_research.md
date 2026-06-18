<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh

## Purpose
This is the multi-file variant of `test_rename.sh`. It creates 100 long-named files and performs intensive within-directory and cross-directory rename cycles for each file.

## Important APIs, Types, and Functions
Important variables are `SUB_DIR1`, `SUB_DIR2`, `FILENAME_1`, `FILENAME_2`, `NB_LOOP_1=10`, `NB_LOOP_2=100`, `NB_FILES=100`, and `ERR`. The command set is `mkdir`, `touch`, `mv`, `ls -li`, and cleanup with `rm -rf`.

## Control Flow
After creating both directories, the script creates 100 files named `FILENAME_1.<index>`. In each outer loop it runs "test 1", where every file is renamed back and forth 100 times inside `SUB_DIR1`. It then runs "test 2", where each file is moved to `SUB_DIR2`, cycled among names and directories 100 times, and returned to `SUB_DIR1`. It removes both child directories and prints the computed rename count.

## State and Persistence Behavior
It mutates many files under a `hercule-$$` parent. As with `test_rename.sh`, cleanup removes the child directories but can leave the parent directory. Most inner failures exit early and leave state for inspection.

## Dependencies and Integration Points
It uses Bash-specific syntax under `/bin/sh`. It stresses NFS-Ganesha rename scalability, directory cache invalidation, and repeated cross-directory moves with many distinct entries.

## Risks and Test Signals
Risks include high operation count, leftover parent directory, no final assertion that all files returned to the expected names, and non-portability to shells such as `dash`. Test signals are zero errors, successful completion of all progress dots, expected rename count, and no stale entries in final server/client listings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh -->
