# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/pre-commit

## Purpose

This Git pre-commit hook enforces clang-format/checkpatch policy and prompts before committing submodule pointer updates.

## Important APIs, Types, and Functions

`handle_unformatted_file` fails commits unless a rebase is in progress. `check_staged_files` runs `clang-format -style=file --dry-run --Werror -` on staged C/C++ files under `src`. Later top-level logic runs `checkpatch.pl --no-signoff -q -` on the staged diff and checks `.gitmodules` paths for staged submodule updates.

## Control Flow

The hook first checks staged source formatting. It chooses a diff base of `HEAD` or the empty tree, runs checkpatch on the staged diff, then lists modified submodules and prompts on `/dev/tty` before allowing the commit.

## State and Persistence Behavior

It does not modify files; it blocks or allows commits. It reads staged content and repository metadata.

## Dependencies and Integration Points

It depends on Bash, git, clang-format, repository `src/scripts/checkpatch.pl`, `.gitmodules`, and an interactive TTY for submodule prompts.

## Risks and Edge Cases

The staged-file loop uses shell word splitting, so filenames with spaces are unsafe. In non-interactive environments, the submodule prompt can fail or hang. The `grep -F "$SUBMODULES"` command with multi-line pattern content can behave unexpectedly. Rebase detection changes formatting failures into warnings.

## Test Signals

Hook tests should stage formatted/unformatted C files, checkpatch violations, no-submodule and submodule changes, initial commit state, rebase state, and non-interactive commits.
