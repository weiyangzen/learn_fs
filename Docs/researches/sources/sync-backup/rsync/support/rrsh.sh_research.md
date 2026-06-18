<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsh.sh -->
# sources/sync-backup/rsync/support/rrsh.sh

Purpose: shell helper for abdiff/testing that emulates sshd forced-command execution of `rrsync DIR`.

Important APIs/types/functions: no functions. It consumes the configured `RRSYNC` executable and restricted `DIR`, strips rsync remote-shell options until `lh` or `localhost`, sets `SSH_ORIGINAL_COMMAND`, and execs rrsync.

Control flow: parse and skip selected ssh-style options (`-l`, other dash options), require a pretend local host, collect the remaining rsync server command, export it as `SSH_ORIGINAL_COMMAND`, and `exec "$RRSYNC" "$DIR"`.

State and persistence behavior: only environment mutation before exec. No files are changed directly.

Dependencies and integration points: depends on `/bin/sh` and an rrsync executable. It lets tests exercise rrsync's parsing path without an actual ssh daemon.

Risks: parser is intentionally minimal and accepts only local pretend hosts. It does not enforce options itself; all restriction semantics are delegated to rrsync.

Test signals: use as rsync `-e "sh rrsh.sh <rrsync> <dir>"` and confirm push/pull commands are passed through `SSH_ORIGINAL_COMMAND` exactly as sshd would provide.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsh.sh -->
