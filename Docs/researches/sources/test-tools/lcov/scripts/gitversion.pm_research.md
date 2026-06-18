# sources/test-tools/lcov/scripts/gitversion.pm

Purpose: git version-script callback that reports the last commit affecting a file, optionally mapped to a git-p4 changelist, with optional dirty-file detection.

Important APIs: package `gitversion` exports `new`, `extract_version`, `compare_version`, and `usage`. Options include `--md5`, `--p4`, `--prefix`, `--allow-missing`, and `--local-change`.

Control flow and state: `extract_version` applies prefix to relative names, checks existence, resolves absolute path, and runs git commands from the containing directory. If the directory is in a git repo and `git log --no-abbrev --oneline -1 <file>` returns a commit, it emits `SHA <commit>` or scans `git show -s` for a `git-p4` changelist and emits `CL <id>`. With `--local-change`, non-empty `git diff <file>` appends edited mtime and optional md5. Non-git files fall back to mtime and optional md5.

Dependencies and integration: uses `annotateutil` helpers and git CLI. `tests/common.mak` selects it as the default `VERSION_SCRIPT` in git checkouts.

Risks and test signals: commands interpolate paths without quoting and use basename from the file directory. Untracked files in git worktrees fall through to mtime. Compare md5 logic is subtle and only applies for fallback/edited strings. Tests include lcov merge version checks, git dirty-file behavior, git-p4 mapping, and wrapper parity.
