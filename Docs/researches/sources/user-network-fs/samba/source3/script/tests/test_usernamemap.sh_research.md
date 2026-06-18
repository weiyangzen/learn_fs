# sources/user-network-fs/samba/source3/script/tests/test_usernamemap.sh

Purpose: verifies `username map` handling for UNIX groups and mapped usernames in an AD member selftest. It checks that a mapped login name authenticates using the target user's password and that an unmapped control user still authenticates normally.

Important functions and APIs: uses `smbclient` wrapped by `VALGRIND` and `subunit.sh`. There are no helper functions; the test is two `testit` invocations against `//SERVER/tmp`.

Control flow: parse `SERVER` and `SMBCLIENT`, source subunit support, then run `smbclient` as `SERVER/jackthemapper` and `SERVER/jacknomapper`, both using the `jacknomapper` password. Both must be able to list the share.

State and persistence: no files are created. It depends entirely on smb.conf username-map state and test users provisioned by the environment.

Dependencies and integration: registered from `selftest/tests.py` as `samba3.blackbox.smbclient_usernamemap` in `ad_member_idmap_nss:local`. It integrates with Samba authentication, domain-qualified usernames, and username-map parsing.

Risks and test signals: credentials are hard-coded for the selftest fixture, so provisioning changes break the test. It is a positive-only test and does not assert that the wrong password fails. Passing signal is successful `ls` for both mapped and unmapped identities.
