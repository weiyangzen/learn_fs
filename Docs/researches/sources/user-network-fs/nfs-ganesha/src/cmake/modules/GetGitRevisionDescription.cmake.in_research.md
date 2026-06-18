# sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake.in

## Purpose

`GetGitRevisionDescription.cmake.in` is the configured helper used to read the active Git HEAD reference or detached commit and expose `HEAD_REF` and `HEAD_HASH` to the parent module.

## Important APIs, Types, and Functions

It uses configured placeholders `@HEAD_FILE@`, `@GIT_DIR@`, and `@GIT_DATA@`. It sets `HEAD_HASH` and conditionally `HEAD_REF`.

## Control Flow

The helper reads the copied HEAD file, strips whitespace, and checks whether it contains a symbolic `ref`. For named branches it removes `ref: `, copies either the ref file or its log into `git-data/head-ref`, and in the log fallback sets `HEAD_HASH` to the ref name. For detached HEAD it copies `.git/HEAD` to `head-ref`. If `HEAD_HASH` was not set, it reads and strips `head-ref`.

## State and Persistence Behavior

It copies Git metadata into the build tree so CMake can track reconfiguration dependencies. It does not directly run Git.

## Dependencies and Integration Points

It is configured and included only by `GetGitRevisionDescription.cmake`. Its output variables are consumed by `get_git_head_revision`.

## Risks and Edge Cases

The branch-log fallback sets `HEAD_HASH` to the ref path rather than parsing the latest hash from the log, which may be intentional for reconfigure tracking but is not a commit hash. The helper does not support linked worktree `.git` files. It limits reads to 1024 bytes, adequate for normal HEAD files.

## Test Signals

Configure from branch, detached HEAD, and a missing direct ref file with log fallback. Inspect generated `CMakeFiles/git-data/head-ref` and returned variables after branch changes.
