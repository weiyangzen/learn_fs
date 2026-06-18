# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_spn.sh

Purpose: blackbox coverage for `samba-tool spn add` and `spn delete` against an existing provisioned DC.

Control flow: it builds `CONFIG` from the supplied prefix, adds and deletes `FOO/bar` for `Administrator`, verifies duplicate SPN add fails for `Guest`, verifies protected or wrong-user deletion fails, adds/deletes the SPN for `Guest`, and verifies deleting a missing SPN or adding for a nonexistent user fails.

State and dependencies: it mutates servicePrincipalName attributes in the target database. It depends on a provisioned `$PREFIX/etc/smb.conf`.

Risks and test signals: because it runs against an existing environment, preexisting `FOO/bar` values would affect results. Expected-failure checks are strong negative-path signals.
