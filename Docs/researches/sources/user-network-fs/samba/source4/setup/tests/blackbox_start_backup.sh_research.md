# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_start_backup.sh

Purpose: verifies Samba refuses to start directly from a database marked as a backup.

Control flow: `do_provision()` creates a DC under `$PREFIX/start-backup`. `add_backup_marker()` uses `ldbmodify` to add `backupDate` to `@SAMBA_DSDB`. `start_backup()` runs `samba --maximum-runtime=5 -i --debug-stdout`, expects a nonzero exit, and greps output for `failed to start: Database is a backup`.

State and dependencies: it creates and removes a provisioned database. It depends on `samba`, `samba-tool`, `ldbmodify`, and common blackbox helper binary lookup.

Risks and test signals: the five-second maximum runtime prevents hangs if the bad condition regresses. The output grep ensures the failure reason is the backup marker, not an unrelated startup error.
