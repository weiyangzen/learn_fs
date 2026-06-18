# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_setpassword.sh

Purpose: blackbox password-management coverage for `samba-tool user setpassword` and domain password settings.

Control flow: it provisions a simple DC, creates `testuser`, sets the password normally, sets it with `--must-change-at-next-login`, repeats with a non-ASCII password, then resets domain password settings to defaults with plaintext storage enabled.

State and dependencies: it mutates a provisioned test database under `$PREFIX/simple-dc`. Dependencies include `samba-tool`, Python, and subunit helpers.

Risks and test signals: it primarily checks CLI success, not subsequent authentication. The non-ASCII password is an important encoding signal; environment locale problems could affect this script.
