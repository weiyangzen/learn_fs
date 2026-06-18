# sources/user-network-fs/samba/source3/script/tests/test_smbd_no_krb5.sh

## Purpose
This test verifies server-side Kerberos disablement: Kerberos access works first, then fails after `gensec:gse_krb5=no`, while NTLM/SPNEGO downgrade still works.

## Important APIs, Functions, and Control Flow
The script accepts `smbclient SERVER USERNAME PASSWORD PREFIX`, resolves `samba4kinit` if available, loads `subunit.sh` and `common_test_fns.inc`, and sets `opt="--option=gensec:gse_krb5=yes -U..."`. It calls `test_smbclient` with `--use-kerberos=required`, writes `global_inject.conf` next to `SMB_CONF_PATH` with `gensec:gse_krb5=no`, verifies `--use-kerberos=required` fails, verifies `--use-kerberos=disabled` succeeds, then clears the config.

## State, Dependencies, Integration, and Risks
State is `global_inject.conf`, which directly affects the test server. It depends on configuration reload behavior and the `tmp` share. The most important risk is leaving the global injection file populated if the script is interrupted before the final clear. Test signals are success, expected failure, and downgrade success through common `test_smbclient` helpers.
