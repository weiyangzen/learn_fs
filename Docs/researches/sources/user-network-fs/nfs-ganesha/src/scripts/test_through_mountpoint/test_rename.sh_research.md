<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh

## Purpose
This test repeatedly renames one long-named file within a directory and across two directories. It targets NFS rename correctness, especially when moving names between sibling directories under an export.

## Important APIs, Types, and Functions
It uses `SUB_DIR1=hercule-$$/depouillement`, `SUB_DIR2=hercule-$$/protections`, two long file names, `NB_LOOP_1=10`, `NB_LOOP_2=100`, and `ERR`. Commands are `mkdir -p`, `touch`, `mv`, `ls -li`, and `rm -rf`.

## Control Flow
The script creates the two directories and one initial file. Each outer pass first does 100 back-and-forth renames inside `SUB_DIR1`. It then moves the file to `SUB_DIR2`, performs 100 cycles of renaming inside `SUB_DIR2`, moving the second name back to `SUB_DIR1`, and moving it again to `SUB_DIR2` under the first name. Finally it moves the file back to `SUB_DIR1` and repeats. It exits immediately on most inner rename failures.

## State and Persistence Behavior
The test creates a `hercule-$$` tree and removes the two child directories at the end. It does not explicitly remove the parent `hercule-$$`, so an empty parent directory can remain after success.

## Dependencies and Integration Points
It depends on Bash arithmetic/conditionals under `/bin/sh`. It integrates with mounted-export rename paths, directory entry invalidation, and cross-directory move behavior.

## Risks and Test Signals
Risks include leftover parent directories, success exit despite some non-fatal `ERR` increments, and no verification of final directory emptiness. Test signals are the reported rename count, zero errors, and successful repeated cross-directory renames without stale name lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh -->
