# sources/user-network-fs/samba/source3/script/tests/test_smbspool_krb.sh

## Purpose
This test verifies Kerberos-backed `smbspool` printing when `AUTH_INFO_REQUIRED=negotiate`, and verifies that printing fails after Kerberos credentials are destroyed.

## Important APIs, Functions, and Control Flow
It accepts server, username, password, and realm, loads `subunit.sh` and `common_test_fns.inc`, resolves `smbspool`, `samba4kinit`, and `samba4kdestroy`, sets `KRB5CCNAME=FILE:$PREFIX/ccache_smbclient_kerberos`, and defines positive/negative helpers that run `smbspool smb://$SERVER/print3 ... example.ps` with `AUTH_INFO_REQUIRED=negotiate`. The script kinit's, runs the positive test, destroys the ccache, removes it, then expects the same print command to fail.

## State, Dependencies, Integration, and Risks
State is the Kerberos ccache and any print job created by the positive test. Dependencies are the KDC, print3 share, CUPS-style AuthInfoRequired behavior, and example PostScript file. Cleanup destroys/removes credentials but does not explicitly inspect print backend state. Test signals are positive zero exit and negative nonzero exit through subunit.
