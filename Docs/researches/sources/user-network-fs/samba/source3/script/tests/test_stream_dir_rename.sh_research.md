# sources/user-network-fs/samba/source3/script/tests/test_stream_dir_rename.sh

## Purpose
This regression test covers Bug 15314: after requesting an invalid stream path below a directory, the directory should still be renameable and not fail with `NT_STATUS_ACCESS_DENIED`.

## Important APIs, Functions, and Control Flow
It accepts server, credentials, prefix, and `SMBCLIENT`, suppresses deprecated warnings, and defines `test_stream_xattr_rename`. The helper writes smbclient commands against `streams_xattr_nostrict`: delete any old directories, create `stream_xattr_test`, upload a file, attempt `get stream_xattr_test/file.txt:abcf`, rename the directory to `stream_xattr_test1`, cleanup, and quit. It fails if the command exits nonzero or output contains `NT_STATUS_ACCESS_DENIED`.

## State, Dependencies, Integration, and Risks
State is a temporary command file and remote directories/files on the streams share. It depends on stream syntax, `streams_xattr_nostrict`, and exact access-denied output. Cleanup is embedded in the command script, so early connection failure can leave remote state. Test signal is successful rename after invalid stream access.
