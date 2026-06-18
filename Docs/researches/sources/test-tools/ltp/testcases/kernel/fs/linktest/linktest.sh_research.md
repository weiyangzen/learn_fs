# sources/test-tools/ltp/testcases/kernel/fs/linktest/linktest.sh

## Purpose

`linktest.sh` is a regression test for creating many hard links and symbolic links to a file.

## Important APIs, Types, and Functions

Modern LTP shell variables define tmpdir use, test function, options `-a` and `-s`, argument parsing, and usage. Functions are `usage`, `parse_args`, `do_link`, and `do_test`.

## Control Flow

`parse_args` validates nonnegative integer link counts. `do_test` creates separate hard-link and symlink directories with source files, then calls `do_link` for symbolic and hard links. `do_link` enters the directory, loops until the requested limit, runs `ln` with the requested options, counts failures, and reports pass only when the error count is zero.

## State and Persistence Behavior

All generated files live in LTP tmpdir directories named with `$$` and are removed at the end of `do_test`.

## Dependencies and Integration Points

Uses `tst_test.sh`, shell `ln`, `touch`, `mkdir`, `rm`, and POSIX filesystem link semantics.

## Risks and Edge Cases

Very high hard-link counts may legitimately exceed filesystem link limits, producing `TFAIL`. Symlink counts mostly stress directory entry creation rather than inode link count. The test does not verify final link count, only `ln` return status.

## Test Signals

Pass is zero errors for both symbolic and hard link loops. The result line reports the number of failed link attempts.
