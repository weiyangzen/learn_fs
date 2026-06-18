# sources/test-tools/ltp/testcases/kernel/fs/ftest/ftest02.c

## Purpose

`ftest02.c` stresses inode and directory operations with several children performing random file creation, unlink/rmdir attempts, directory creation, nested file creation, and sync operations.

## Important APIs, Types, and Functions

Key functions are `crfile`, `unlfile`, `fussdir`, `dotest`, `dowarn`, `term`, and `cleanup`. `ft_mkname` generates deterministic names by child and iteration. State includes `dirname`, `homedir`, `iterations`, `nchild`, `pidlist`, optional mount variables, and `local_flag`.

## Control Flow

`main` sets defaults, creates separate work and home directories under an LTP tempdir, forks children, and waits for all. Each child runs `dotest`, which picks randomly among create-file, unlink-file, directory-fuss, and `sync`. After wait, the parent removes generated files and directories, then removes the work trees with `/bin/rm -rf`.

## State and Persistence Behavior

Each child creates names under the shared `dirname` but uses child-specific name prefixes. `crfile` creates sparse files by seeking up to 1 MiB before writing and then verifies the written message. `fussdir` intentionally checks that `rmdir` on a non-empty directory fails, then removes nested files and may leave the directory for later cleanup.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, `libftest`, fork/wait, `open`, `lseek`, `write`, `read`, `mkdir`, `rmdir`, `unlink`, `chdir`, `sync`, optional `umount`, and `/bin/rm`.

## Risks and Edge Cases

There is vestigial mount cleanup for `partition`/`fstyp` that is not initialized by the default path. Error handling is aggressive and many expected races become `TBROK`. `dirname` is temporarily overwritten inside `fussdir`, so unexpected control-flow exits could leave global path state inconsistent.

## Test Signals

Pass is all children exiting with zero and the fork/wait section reporting `TPASS`. Failures identify the child and operation through `dowarn` or explicit non-empty-directory checks.
