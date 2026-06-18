# sources/user-network-fs/samba/source3/script/tests/test_worm.sh

Purpose: tests WORM VFS behavior around deletion and overwrite protection after the configured grace period, including ctime refresh handling and rename-over protection.

Important functions and APIs: uses forced-interactive `smbclient`, local filesystem checks, `touch`, `chmod`, and subunit. `do_cleanup()` removes test files and temporary command files. `test_worm()` performs the full scenario.

Control flow: the test uploads several files to the `worm` share and immediately deletes one, which should be allowed. After sleeping one second, it tries POSIX chmod and delete operations on protected files, refreshes ctime for one file, and validates that the protected file remains. It then uploads a sentinel value and attempts `rename ... -f` over a protected file, verifying original contents are unchanged. If running as root, it also checks the ctime-refreshed file was deleted.

State and persistence: creates and deletes files in `$LOCAL_PATH/worm`, command files under `$PREFIX`, and a sentinel file. Cleanup removes expected artifacts.

Dependencies and integration: registered for both NT1 and SMB3 in the `fileserver` environment. It depends on a WORM share with short grace-period behavior and on the client supporting POSIX commands for the relevant protocol path.

Risks and test signals: the one-second sleep encodes timing expectations and can be flaky if filesystem timestamp granularity or VFS settings change. Strong signals are protected deletion refusal, successful recent-file deletion, and no overwrite through forced rename.
