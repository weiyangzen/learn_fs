# sources/user-network-fs/samba/source3/script/tests/test_symlink_dosmode.sh

## Purpose
This test verifies that listing a local symlink through `smbclient` reports the expected DOS mode `N`.

## Important APIs, Functions, and Control Flow
It accepts server/IP/credentials/local path/prefix/smbclient, suppresses deprecated warnings, prepares `$LOCAL_PATH/testdir/dir/symlink` pointing to `../file`, then `test_symlink_dosmode` writes `ls testdir/dir/*` and runs `smbclient //$SERVER/local_symlinks -I$SERVER_IP`. It extracts the mode field from the symlink listing using `awk '/symlink/ {print $2}'` and compares it with `N`.

## State, Dependencies, Integration, and Risks
State is a local fixture under the share path, removed after the test. It depends on Unix symlink support, the `local_symlinks` share, and stable listing columns. Risks include cleanup failure if permissions or command errors intervene. Test signal is exact parsed mode plus successful smbclient command.
