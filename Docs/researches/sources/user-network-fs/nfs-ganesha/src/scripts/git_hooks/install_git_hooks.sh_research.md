# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/install_git_hooks.sh

## Purpose

`install_git_hooks.sh` installs repository Git hooks and checkpatch configuration into the current checkout.

## Important APIs, Types, and Functions

Top-level shell logic determines `CURDIR`, `TOPDIR`, and `HOOKDIR`; symlinks `src/scripts/checkpatch.conf` to `.checkpatch.conf`; copies `pre-commit` and `commit-msg` into `.git/hooks`; and marks them executable.

## Control Flow

The script handles macOS by using `greadlink -m`; otherwise it uses `readlink -m`. It resolves the git top-level directory, then performs symlink/copy/chmod operations.

## State and Persistence Behavior

It persistently modifies the local checkout's `.git/hooks` and top-level `.checkpatch.conf` symlink.

## Dependencies and Integration Points

It depends on Bash, `git`, `readlink` or `greadlink`, `ln`, `cp`, and `chmod`. It installs the hooks researched in this subset.

## Risks and Edge Cases

It overwrites existing hooks without backup. The checkpatch symlink target is relative and assumes invocation from a normal repository layout. macOS requires GNU readlink as `greadlink`.

## Test Signals

Run in a temporary git repository and verify hook files and executable bits. Tests should cover preexisting hooks and macOS/Linux path resolution if supported.
