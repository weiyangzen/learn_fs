# sources/test-tools/kdevops/scripts/workflows/fstests/remove-common-failures.sh

## Purpose
Removes failures listed in an expunge directory's `all.txt` from each per-section expunge file.

## Important APIs and control flow
The script validates exactly one directory argument, requires `$DIR/all.txt`, builds an alternation of first-column entries from `all.txt`, then filters each non-`all.txt` file through `grep -E -v`, sorting and deduplicating results.

## State and persistence
Rewrites each expunge file in place via a temporary file. If running inside a Git worktree and a file becomes empty, it runs `git rm -f` on that file.

## Dependencies and integration
Requires `find`, `grep`, `awk`, `sort`, `uniq`, `du`, `mktemp`, and optionally Git. Called by `lazy-baseline.sh`.

## Risks and test signals
The alternation regex is not escaped, so special regex characters in test names or comments can overmatch. The same temp file is moved repeatedly and relies on `mktemp` path reuse semantics. Test with fixture expunge files and verify only all.txt entries are removed.
