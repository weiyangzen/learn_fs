# Research: sources/user-network-fs/samba/source4/selftest/tests_win.sh

Purpose: entry point for legacy Windows VM selftests. It refuses to run unless executed as root, without socket wrapper, and with a readable `WINTESTCONF`.

Important behavior: after validation it exports `WINTEST_DIR=$SRCDIR/selftest/win`, preserves `TMPDIR` and `NETBIOSNAME`, sources the configured Windows test file, and delegates to `$SRCDIR/selftest/test_win.sh`.

State and dependencies: state comes entirely from the sourced config and the remote VM. Dependencies include root privileges, real networking, `WINTESTCONF`, and scripts under `selftest/win`. It integrates with the broader selftest runner as the gate before Windows-oriented tests are allowed to touch the VMware-backed host.

Risks and test signals: unquoted variable tests such as `[ ! $WINTESTCONF ]` are fragile if values contain whitespace or shell metacharacters. It deliberately blocks socket wrapper because Windows VMs require real network access. A useful signal is early, explicit failure before any VM mutation when prerequisites are absent.
