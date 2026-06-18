# sources/user-network-fs/samba/source3/script/tests/test_smbclient_machine_auth.sh

## Purpose
This test checks `smbclient --machine-pass` authentication against normal and force-user/group shares.

## Important APIs, Functions, and Control Flow
The script accepts `SERVER SMBCLIENT CONFIGURATION`, sets global variables consumed by `common_test_fns.inc` (`CONFIGURATION` and lowercase `smbclient`), and runs three `test_smbclient` calls against `tmp`, `forceuser`, and `forcegroup` on port 139 with `--machine-pass`.

## State, Dependencies, Integration, and Risks
No files are created. It depends on a valid machine account secret in the test environment, NetBIOS port 139, and selftest shares whose force-user/group settings are meant to work with machine auth. It exits with the raw `failed` count rather than `testok`, so callers should interpret nonzero exit status. Risks are mostly environment-coupled: stale machine passwords or changed share ACLs break all cases.
