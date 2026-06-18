# sources/user-network-fs/samba/source3/script/tests/test_smbclient_netbios_aliases.sh

## Purpose
This test verifies Kerberos access through an SMB server name that may be supplied as a NetBIOS alias.

## Important APIs, Functions, and Control Flow
It accepts `smbclient SERVER USERNAME PASSWORD PREFIX CONFIGURATION`, resolves `samba4kinit`, creates `KRB5CCNAME=FILE:$PREFIX/test_smbclient_netbios_aliases_krb5ccache`, loads `subunit.sh` and `common_test_fns.inc`, obtains a ticket with `kerberos_kinit`, then calls `test_smbclient "smbclient (krb5)" "ls" "//$SERVER/tmp" --use-krb5-ccache=$KRB5CCNAME`.

## State, Dependencies, Integration, and Risks
State is the Kerberos ccache path, removed before and after the test. It depends on correct SPN/alias setup, test KDC behavior, and the `tmp` share. `ADDADS` is assigned from extra args but not used, suggesting either historical compatibility or a typo. The signal is successful Kerberos-backed `ls` through the provided server name.
