# sources/user-network-fs/samba/source3/script/tests/test_smbclient_kerberos.sh

## Purpose
This test validates `smbclient` Kerberos option handling against a temporary share, including required, desired, off, explicit ccache, and no-user/password modes. It also accounts for FIPS targets where non-Kerberos authentication is expected to fail.

## Important APIs, Functions, and Control Flow
The script loads `subunit.sh` and `common_test_fns.inc`, resolves `samba4kinit`/`samba4kdestroy` if present, sets `KRB5CCNAME=FILE:$PREFIX/ccache_smbclient_kerberos`, and uses `test_smbclient`/`test_smbclient_expect_failure`. It first tests password-based SMB3 connections with different `--use-kerberos` values, branches on `TARGET` for the `off` case, obtains a ticket with `kerberos_kinit`, then tests `--use-krb5-ccache` and ticket-backed desired/required modes.

## State, Dependencies, Integration, and Risks
Persistent state is a Kerberos ccache removed at the end. Dependencies include a working KDC, realm, generated selftest credentials, `common_test_fns.inc`, and Samba Kerberos wrappers. Cleanup uses `kdestroy` and `rm -rf`. Risks include leaked ccaches on early shell interruption and target-name coupling for FIPS semantics. Test signals are subunit results per Kerberos mode.
