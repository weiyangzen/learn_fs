# sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption_off.sh

## Purpose
This shell blackbox test verifies `smbclient` behavior when server-side encryption is globally disabled. It checks that unencrypted access still works for shares whose `smb encrypt` is default/enabled or desired, and that access fails when a share requires encryption or when the client requires encryption.

## Important APIs, Functions, and Control Flow
The script consumes `USERNAME PASSWORD SERVER SMBCLIENT`, wraps the binary with `$VALGRIND`, loads `subunit.sh`, and uses `testit` plus `testit_expect_failure`. The main body is a fixed matrix over shares `enc_desired`, `tmp`, and `tmpenc`, dialects default/SMB1, `-m smb3_02`, and `-m smb3_11`, and optional `--client-protection=encrypt`.

## State, Dependencies, Integration, and Risks
It relies on selftest shares configured with different encryption policies and on `smbclient` returning nonzero for failed tree connects. It has no persistent state except subunit output and the `failed` counter. Risks are mostly configuration drift: if share names or global encryption settings change, the expected success/failure polarity inverts. Test signals are explicit subunit pass/fail entries and final `testok`.
