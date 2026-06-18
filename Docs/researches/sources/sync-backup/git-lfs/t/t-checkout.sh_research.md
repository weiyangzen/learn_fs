# sources/sync-backup/git-lfs/t/t-checkout.sh

## Purpose
Comprehensive integration tests for `git lfs checkout`. It validates normal checkout, path filtering, subdirectory context, missing local data, filesystem conflicts, symlinks, hardlinks, permissions, merge-conflict extraction, sparse/partial clone behavior, pointer extensions, and bare/worktree edge cases.

## Important APIs, Functions, and Control Flow
The main test creates repeated LFS objects across files and directories, removes worktree files, and exercises `git lfs checkout` with no args, file args, globs, `.` and `..`, and directory filters. Subsequent tests cover file/directory and symlink conflicts, case-insensitive collisions, modified files, hardlink replacement, missing clean filter, outside/bare repositories, read-only files/directories, mtime preservation for empty files, conflict checkout with `--to --base/--ours/--theirs`, `GIT_WORK_TREE`, sparse partial clone, and extension smudge paths.

## State, Persistence, and Dependencies
The script heavily mutates worktrees, indexes, `.git/lfs/objects`, incomplete checkouts, permissions, symlinks, hardlinks, merge state, environment variables, and Git config. Dependencies include many `testlib.sh` helpers, `lfstest-nanomtime`, version gates, `setup_case_inverter_extension`, `has_native_symlinks`, and object assertions.

## Integration Points, Risks, and Test Signals
Integration includes checkout scanner behavior, Git index state, pointer decoding, clean/smudge filters, sparse checkout Git versions, filesystem safety checks, and extension smudge execution. Signals are worktree content comparisons, clean-index/status assertions, progress lines, skip/error logs, `fsck`, and non-advancing HEAD on failure. Risks are platform-specific symlink/permissions/case behavior and version-dependent sparse-index behavior.
