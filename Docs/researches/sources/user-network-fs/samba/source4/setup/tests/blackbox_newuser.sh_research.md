# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_newuser.sh

Purpose: blackbox test for `samba-tool user create`, `enable`, `setpassword`, and `setexpiry`.

Control flow: it provisions a simple DC, builds `CONFIG` for that target, creates `NewUser` with many profile/contact attributes and `NewUser1` with `--use-username-as-cn`, enables both accounts, changes both passwords, sets no-expiry, and then sets a seven-day expiry.

State and dependencies: it creates `$PREFIX/simple-dc` and mutates its `sam.ldb`. It depends on subunit helpers, `$PYTHON`, `$BINDIR/samba-tool`, and NTVFS provisioning.

Risks and test signals: assertions are command-exit based rather than LDAP attribute verification, so regressions that accept but mishandle attributes may escape. It still provides useful CLI parsing and account lifecycle smoke coverage.
