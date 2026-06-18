# sources/sync-backup/rsync/rsync-web/bin/upload

Purpose: Website upload helper for the rsync HTML hierarchy.

Important APIs, types, and functions: Checks for an `rsync-and-debian` directory as a root marker, then runs `rsync -aviOHFFc --del -f._filt . $SAMBA_HOST:/home/httpd/html/rsync/ "$@"`.

Control flow: Single guard: if run from the expected web root, upload; otherwise print an error and exit 1. Extra script arguments are appended to the rsync command.

State and persistence behavior: Mutates the remote web tree and deletes remote files not present locally due to `--del`. No local persistent state.

Dependencies and integration points: Depends on rsync, filter file `_filt`, `$SAMBA_HOST`, and the local website checkout layout.

Risks and test signals: Risks are destructive remote deletion, unvalidated destination, and accidental extra args. Test in staging with `--dry-run`, validate filter behavior, and verify root marker prevents accidental uploads from wrong directories.
