# sources/sync-backup/rsync/rsync-web/bin/badge-update

Purpose: Small deployment helper that refreshes the GitHub Actions build badge on the rsync website.

Important APIs, types, and functions: Shell commands remove `badge.svg`, fetch a fresh badge with `wget`, and upload it with `rsync -aiic --inplace --remove-source-files` to `$SAMBA_HOST:/home/httpd/html/rsync/`.

Control flow: Linear script with no argument parsing or error handling beyond shell command exit behavior.

State and persistence behavior: Deletes and recreates local `badge.svg`, then removes it after successful rsync upload because `--remove-source-files` is used.

Dependencies and integration points: Depends on `wget`, `rsync`, network access to GitHub, and `$SAMBA_HOST` credentials/path. Integrates with rsync-web publishing workflow.

Risks and test signals: Risks include unvalidated `$SAMBA_HOST`, failed/partial download uploaded as badge, and no `set -e`. Test by running in a staging directory with a staging host and verifying uploaded SVG content.
