# sources/sync-backup/git-lfs/t/t-dedup.sh

## Purpose

Exercises `git lfs dedup` capability checks, safety checks, and output reporting. It confirms deduplication is refused when LFS clean/smudge extensions are configured, succeeds or skips gracefully for tracked files, supports `--test`, and rejects dirty working trees.

## Important APIs, control flow, and dependencies

The tests initialize repositories, set and unset `lfs.extension.foo.clean`, `smudge`, and `priority`, run `git lfs dedup` and `git lfs dedup --test`, track `*.dat`, commit files, manually remove one local media object from `.git/lfs/objects/<oid-prefix>/<oid>`, and inspect command output. They branch early when the platform reports no deduplication support.

## State, dependencies, integration points, risks, and test signals

State under test is the working tree cleanliness, Git config extension state, LFS pointer/object cache state, and platform dedup support. Integration points are filesystem clone/reflink/hardlink-style dedup support, extension configuration loading, local object lookup, and the dirty-worktree guard. Risks include dedup running with extensions that transform content, restoring or skipping missing media inconsistently, and modifying an uncommitted working tree. Signals are exact messages for unsupported extension use, support confirmation from `--test`, `Success:` or `Skipped:` rows for files, and the dirty-tree error.
