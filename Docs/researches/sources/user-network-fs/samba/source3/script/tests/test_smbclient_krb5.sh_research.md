# sources/user-network-fs/samba/source3/script/tests/test_smbclient_krb5.sh

## Purpose
This compact wrapper checks that Samba 3 `smbclient` can access `//$SERVER/tmp` with an externally supplied Kerberos ccache.

## Important APIs, Functions, and Control Flow
It accepts `ccache smbclient3 server` plus optional `smbclient` args, exports `KRB5CCNAME`, loads `subunit.sh`, and runs one `testit "smbclient"` invoking `$VALGRIND $SMBCLIENT3 //$SERVER/tmp -c 'ls' --use-krb5-ccache=$KRB5CCNAME $ADDARGS`.

## State, Dependencies, Integration, and Risks
The script does not create the ccache; the caller must provide it. It depends on the share `tmp`, a valid ticket, and correct `ADDARGS` from the surrounding selftest environment. The `failed` variable is incremented without being initialized locally, relying on shell empty-to-zero behavior in `expr`. The only test signal is the command exit status reported through subunit.
