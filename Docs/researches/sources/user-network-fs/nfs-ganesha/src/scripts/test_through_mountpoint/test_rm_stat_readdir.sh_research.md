<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh

## Purpose
This mountpoint test validates consistency between create, getattr/stat, readdir, remove, negative lookup, and readdir-after-remove. It is more assertive than the simpler create/unlink tests because it checks both positive and negative visibility.

## Important APIs, Types, and Functions
The script uses `SUB_DIR1=TESTDIR_RMSTAT-$$`, `FILENAME_1`, `FILENAME_2`, `NB_FILES=1000`, and `ERR`. It uses `touch`, `stat`, `ls`, `egrep`, `rm`, and `rm -rf`.

## Control Flow
The first phase creates 500 pairs of files, checking for each first file that `stat` succeeds before readdir membership, and for each second file that readdir membership succeeds before `stat`. The second phase removes each pair, checks that direct lookup via `ls -l` returns exit code 2, and checks that the removed names no longer appear in directory listings. The final phase recreates the same pairs and repeats the positive stat/readdir checks before cleanup.

## State and Persistence Behavior
Temporary state lives under `TESTDIR_RMSTAT-$$` and is removed at normal completion. The script accumulates errors but still exits with the status of the final commands rather than explicitly failing on `ERR`.

## Dependencies and Integration Points
It requires Bash-style syntax and standard Unix tools. It integrates with NFS-Ganesha lookup cache, directory cache, remove, getattr, and readdir behavior.

## Risks and Test Signals
Risks include assuming GNU/coreutils `ls -l missing` returns `2`, unquoted path variables, slow execution on large directories, and no explicit nonzero exit for accumulated errors. Strong test signals are zero reported errors, removed names absent from readdir, missing names returning ENOENT-like status, and successful recreate after removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh -->
