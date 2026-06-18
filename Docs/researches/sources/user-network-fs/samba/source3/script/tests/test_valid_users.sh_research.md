# sources/user-network-fs/samba/source3/script/tests/test_valid_users.sh

Purpose: blackbox check that a share guarded by the `valid users` smb.conf parameter can be listed by a permitted user.

Important functions and APIs: uses forced-interactive `smbclient` and `subunit.sh`. `test_valid_users_access()` writes an input file containing `ls` and `quit`, runs `smbclient //SERVER/share -I SERVER_IP -UUSERNAME%PASSWORD`, then checks for the expected interactive prompt marker.

Control flow: after parsing server, domain, credentials, prefix, and smbclient path, the script invokes `test_valid_users_access valid-users-access` through `testit` and exits with the failure count.

State and persistence: creates a temporary command file under `$PREFIX` and removes it after the client run. It does not modify server state.

Dependencies and integration: registered under the `fileserver` loop in `selftest/tests.py` as `samba3.blackbox.valid_users`. It depends on the share `valid-users-access` being configured with access for the provided test user.

Risks and test signals: the success check uses prompt text, not a specific directory listing, so prompt-format changes can affect it. A nonzero smbclient exit or missing prompt is the failure signal.
