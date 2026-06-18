# sources/user-network-fs/samba/source3/script/tests/test_timestamps.sh

## Purpose
This test verifies `smbclient allinfo` reports nontrivial timestamps correctly, including epoch zero, negative epoch seconds, and a pre-1970 date.

## Important APIs, Functions, and Control Flow
It accepts server IP, credentials, prefix, and `SMBCLIENT`, exports `TZ=GMT`, and defines `setup_testfiles`, `remove_testfiles`, and `test_time`. Setup uses `touch -d "$(date --date=@0)"`, `@-1`, `@-2`, and `touch -t 196801010000`. `test_time` calls `smbclient //$SERVER/tmp -c "allinfo $file"` and verifies `access_time` and `write_time` lines contain the expected formatted string, ignoring synthesized `create_time`.

## State, Dependencies, Integration, and Risks
State is four files under `$PREFIX` exposed by the `tmp` share, removed at the end. It depends on GNU `date --date=@...`, filesystem support for negative timestamps, timezone formatting, and exact `smbclient allinfo` strings. Risks include platform-specific date formatting and cleanup not running after early failure. Test signals are exact timestamp greps for access and write times.
