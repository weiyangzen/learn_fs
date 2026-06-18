# sources/user-network-fs/samba/source3/script/tests/test_smbtorture_nocrash_s3.sh

## Purpose
This wrapper runs one `smbtorture` test and asserts that `smbd` does not log an additional panic during the run.

## Important APIs, Functions, and Control Flow
It accepts `TEST UNC USERNAME PASSWORD SMBTORTURE` plus extra args, loads `subunit.sh`, counts `PANIC` lines in `$SMBD_TEST_LOG`, runs `$VALGRIND $SMBTORTURE $unc -U"$username"%"$password" $ADDARGS $t`, recounts panics, then uses `testit "check_panic" test $panic_count_0 -eq $panic_count_1`.

## State, Dependencies, Integration, and Risks
State is only log observation, plus debug writes to `/tmp/look`. It depends on `$SMBD_TEST_LOG` and stable panic logging. Risks include shared log noise from other tests and `/tmp/look` collisions. Test signals are smbtorture exit status and unchanged panic count.
