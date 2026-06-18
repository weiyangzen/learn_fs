# sources/sync-backup/casync/test/pseudo-ssh

Purpose: minimal SSH replacement for local remoting tests.

Important APIs/types/functions: shell script shifts away the hostname-style argument and `exec`s the remaining command locally.

Control flow/state: no persistent state; process is replaced with the requested command.

Dependencies/integration: `test-script.sh.in` sets `CASYNC_SSH_PATH` to this script and `CASYNC_REMOTE_PATH` to the built casync binary to exercise SSH locator logic without real SSH.

Risks/test signals: only models command execution, not authentication, quoting, network I/O, or remote environment differences. It is appropriate for protocol path plumbing tests.

Source research group: `subset-b-009122`.
