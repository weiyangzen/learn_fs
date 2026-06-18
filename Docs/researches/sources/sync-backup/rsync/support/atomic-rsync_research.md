<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/atomic-rsync -->
# sources/sync-backup/rsync/support/atomic-rsync

Purpose: Python wrapper that performs a pull-style rsync update into a new hard-linked tree and then swaps it into place, approximating an atomic directory update.

Important APIs/types/functions: `main()`, `atomic_symlink()`, `usage_and_exit()`, and `die()`. Constants include `ALT_DEST_ARG_RE`, which blocks user-supplied `--link-dest`, `--compare-dest`, and `--copy-dest` variants, and `RSYNC_PROG = /usr/bin/rsync`.

Control flow: parse command-line rsync arguments, require an existing local destination directory, reject alternate-dest options, parse allowed rsync exit codes from `ATOMIC_RSYNC_OK_CODES`, decide whether the destination is a `*-1`/`*-2` symlink rotation or a `~new~`/`~old~` directory swap, delete stale staging directories, run rsync with `--link-dest=<current dest>`, and then either rename a newly created symlink over the live link or rename current/new directories.

State and persistence behavior: creates and deletes sibling staging directories, updates symlinks with `os.rename()`, and preserves the prior destination until the next run. It dereferences the destination with `realpath()` and forbids `/` as the destination.

Dependencies and integration points: depends on Python 3, `/usr/bin/rsync`, filesystem hard links, and rsync's `--link-dest`. It is intended for local pull destinations rather than arbitrary push deployments.

Risks: the non-symlink `~old~`/`~new~` path is a rapid double rename, not a fully atomic switch. Existing `~old~` and `~new~` directories are removed. The symlink-rotation mode assumes link text suffix and real target suffix stay synchronized. Exit-code allowance defaults to treating vanished files as acceptable, which may hide real partial-copy problems if operators broaden the environment variable too far.

Test signals: tests should cover symlink rotation, plain directory rotation, rejection of alternate-dest options, `/` rejection, failed rsync return handling, and custom `ATOMIC_RSYNC_OK_CODES` parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/atomic-rsync -->
