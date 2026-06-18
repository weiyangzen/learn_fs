<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/munge-symlinks -->
# sources/sync-backup/rsync/support/munge-symlinks

Purpose: recursively add or remove rsync daemon's symlink-munging prefix `/rsyncd-munged/` from symlink targets.

Important APIs/types/functions: `main()`, `find_symlinks()`, `process_one_arg()`, constants `SYMLINK_PREFIX` and `PREFIX_LEN`, and argparse flags `--munge`, `--unmunge`, and `--all`.

Control flow: for each argument, process it if it is a symlink or recursively scan it if it is a directory; read each link target; in unmunge mode remove one prefix or all repeated prefixes with `--all`; in munge mode add the prefix unless already munged or `--all` forces another; replace the symlink by unlinking and recreating it; print the resulting mapping.

State and persistence behavior: mutates symlink objects in place. Directory traversal does not follow symlinks as directories.

Dependencies and integration points: depends on Python 3 and filesystem symlink support. It aligns with rsyncd.conf's `munge symlinks` behavior.

Risks: unlink/recreate is not atomic, so a failed recreate can leave the symlink missing. Permissions or races in writable directories can affect correctness. Non-symlink non-directory arguments are only reported to stderr, not fatal.

Test signals: temporary symlink trees should cover munge, unmunge, repeated prefixes with and without `--all`, directory recursion, and recreate failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/munge-symlinks -->
