<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/instant-rsyncd -->
# sources/sync-backup/rsync/support/instant-rsyncd

Purpose: interactive bash helper that creates and starts a simple unprivileged rsync daemon serving one writable module rooted in the current directory.

Important APIs/types/functions: no shell functions; important generated files are `rsyncd.conf`, optional `<module>.secrets`, `start`, `stop`, `rsyncd.log`, and `rsyncd.pid`.

Control flow: prompt or read arguments for module, port, auth user, and rsync path; create the module directory; write a minimal daemon config with `use chroot = no`; optionally prompt for a password and write a protected secrets file; generate start/stop scripts; start the daemon; print log output and an `rsync://user@host:port/module/` URL; then run `rsync --list-only` as a smoke test.

State and persistence behavior: creates a module directory and several control/config files in the current directory, starts a background daemon, and leaves start/stop scripts for later operation.

Dependencies and integration points: depends on bash, rsync daemon mode, hostname, local filesystem permissions, and optional rsync daemon auth. It is a test/reproduction aid for daemon-related issues.

Risks: creates a writable module with `read only = false` and `use chroot = no`, so it is unsuitable as a hardened production config without edits. It uses unsanitized module/user values in generated config. Existing files with the same names can be overwritten or cause confusing state.

Test signals: create a temporary directory, run with explicit module/port/no auth and with auth, verify generated config, start/stop scripts, pid behavior, and successful `--list-only` connection.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/instant-rsyncd -->
