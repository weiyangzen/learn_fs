# sources/user-network-fs/samba/source3/script/tests/test_smbtorture_s3.sh

## Purpose
This minimal wrapper runs a specified `smbtorture` test against a UNC with supplied credentials and passes through additional torture arguments.

## Important APIs, Functions, and Control Flow
It validates `TEST UNC USERNAME PASSWORD SMBTORTURE`, loads `subunit.sh`, and performs one `testit "smbtorture"` command: `$VALGRIND $SMBTORTURE $unc -U"$username"%"$password" $ADDARGS $t`. It finalizes with `testok`.

## State, Dependencies, Integration, and Risks
The script creates no local state. It depends entirely on the requested smbtorture test, UNC, credentials, and extra args supplied by the selftest harness. Risks are low in the wrapper but high in caller configuration: no additional output validation is done beyond process status. The test signal is the smbtorture exit code.
