# sources/user-network-fs/samba/source3/script/tests/test_smbpasswd.sh

## Purpose
This test covers local SMB user creation, remote password change, and deletion via `smbpasswd` under the selftest uid wrapper.

## Important APIs, Functions, and Control Flow
It accepts `SERVER SERVER_IP USERNAME PASSWORD`, resolves `$BINDIR/texpect` and `$BINDIR/smbpasswd`, and uses test account `alice_smbpasswd`. `create_local_smb_user` writes a texpect script for new/retype password prompts and runs `smbpasswd -a` as uid/euid 0 using `UID_WRAPPER_INITIAL_RUID/EUID`. `test_smbpasswd` gets the user's uid, writes a change-password expect script, runs `smbpasswd -r $SERVER` as that uid, and greps for `Password changed for user`. `delete_local_smb_user` runs `smbpasswd -x`.

## State, Dependencies, Integration, and Risks
State is a local Unix/SMB test user and temporary expect scripts under `$PREFIX`. It depends on uid_wrapper, nss/getent visibility, prompt strings, and the server password-change path. Risks include leaving the test user if creation or password change fails before deletion and brittle prompt matching. Test signals are subunit cases for create/change/delete.
