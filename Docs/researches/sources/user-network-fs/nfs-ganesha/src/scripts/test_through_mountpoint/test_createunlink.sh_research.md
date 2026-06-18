<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh

## Purpose
This mountpoint smoke test repeatedly creates and unlinks one file, then creates it once more and verifies lookup/getattr and readdir visibility before removal. It focuses on stale negative/positive cache behavior around a single name.

## Important APIs, Types, and Functions
Variables include `SUB_DIR1=create_unlink-$$`, `FILENAME`, `NB_ITER_1=100`, `NB_ITER_2=10`, and `ERR`. It uses `touch`, `rm -f`, `ls -li`, and shell existence tests.

## Control Flow
For each of 10 outer iterations, the script performs 100 create/unlink cycles, checking before each create that the file is absent. It then creates the file, runs 100 cycles of `ls -li` on the file and containing directory, removes the file, and proceeds to the next outer iteration.

## State and Persistence Behavior
Temporary state is created under `create_unlink-$$`. The script does not remove the temporary directory at the end, so a successful run leaves an empty directory unless cleaned externally. No durable metadata is written outside the mount.

## Dependencies and Integration Points
It depends on Bash-specific conditionals/arithmetic under a `/bin/sh` shebang. It exercises server-side create, remove, lookup, getattr, and readdir semantics through standard client utilities.

## Risks and Test Signals
Risks include final directory leakage, no failure exit based on `ERR`, and false confidence because it does not verify that `ls` output contains exactly the expected entry. Test signals are zero errors and absence of stale file visibility after unlink in both direct lookup and directory listing paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh -->
