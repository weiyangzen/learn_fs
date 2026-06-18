<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/githooks/pre-push -->
# sources/storage-engines/rocksdb/githooks/pre-push

## Purpose

`githooks/pre-push` is a developer-side Git hook that blocks pushes on two common issues: untracked source files inside tracked directories and formatting failures from `make check-format`. It is intended to catch local mistakes before code reaches CI.

## Important APIs, Types, and Functions

- Bash with `set -e`.
- TTY/automation gate: exits unless stdout is a terminal or `ROCKSDB_FORMAT_HOOK` is set.
- `git ls-files --others --exclude-standard` finds untracked files.
- `grep -E '\.(cc|cpp|c|h|hpp|java|py|mk|sh)$'` limits suspects to source-like extensions.
- A loop checks whether the top-level directory is tracked before reporting the untracked file.
- `make check-format` enforces formatting.
- `FAILED` accumulates whether any check failed and becomes the exit code.

## Control Flow

The hook first skips non-interactive pushes unless explicitly enabled. It gathers suspect untracked files outside `third-party/` whose top-level directory is already tracked, prints a blocking message if any are found, and sets `FAILED=1`. It then always runs `make check-format`; a failure prints remediation guidance and sets `FAILED=1`, while success prints a clean message. The script exits with the accumulated status.

## State and Persistence Behavior

The hook does not modify repository state. It reads Git index/worktree state and runs the format checker, which should be read-only. It can prevent a push by exiting nonzero.

## Dependencies and Integration Points

It depends on Git, grep, sed, head, make, and the RocksDB `check-format` target. Comments note it becomes active via `make all` / `make check` setting `core.hooksPath`. It integrates with developer pushes and can be bypassed with `git push --no-verify`.

## Risks and Edge Cases

Because `set -e` and pipelines are used without `pipefail`, failures inside some pipeline elements may not behave as expected, while `grep` no-match behavior in command substitution is usually tolerated by the assignment. Filenames with unusual newlines are not handled robustly. The TTY gate means CI/automated pushes skip the hook unless `ROCKSDB_FORMAT_HOOK` is set. Running `make check-format` on every interactive push can be slow but gives strong local signal.

## Test Signals

Signals include hook exit zero with clean tree/format, nonzero with untracked source files in tracked directories, ignoring `third-party` untracked files, nonzero on format failures, skip behavior in non-TTY contexts, and forced execution via `ROCKSDB_FORMAT_HOOK=1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/githooks/pre-push -->
