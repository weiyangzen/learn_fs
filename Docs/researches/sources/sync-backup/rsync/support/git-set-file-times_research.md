<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/git-set-file-times -->
# sources/sync-backup/rsync/support/git-set-file-times

Purpose: set checked-out file mtimes to the commit time of the last Git commit that changed each file, optionally listing what would change.

Important APIs/types/functions: `main()`, `print_line()`, `NULL_COMMIT_RE`, and argparse options `--git-dir`, `--tree`, `--prefix`, `--quiet`, `--list`, and file filters.

Control flow: locate `.git` from `git rev-parse` when not supplied, list tracked files from either `git ls-files -z` or `git ls-tree -z -r --name-only`, remove modified working-tree files from the mutation set unless listing, stream `git log -r --name-only --format=... -z --no-renames`, and for each commit-time/file batch still in scope either print current-vs-target time or call `os.utime(..., follow_symlinks=False)`.

State and persistence behavior: mutates mtimes of unmodified tracked files in the working tree, never follows symlinks for timestamp setting, and stops once all target files have been resolved. Modified files retain their current mtimes.

Dependencies and integration points: depends on Python 3, Git CLI, UTC datetime formatting, and a Git checkout or explicit tree. It is useful for reproducible exported trees and rsync workflows that care about mtimes.

Risks: it ignores renames, so renamed files take the last commit that touched the current path. The `git status -z` parsing assumes porcelain status width and may not handle every status combination. `--tree` with `--prefix` can target paths outside the current checkout if misused.

Test signals: run on a small repository with modified and unmodified files, symlinks, file subset filters, `--list` and `--list --list`, explicit `--tree`, and renamed files to document expected no-renames behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/git-set-file-times -->
