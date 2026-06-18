# sources/user-network-fs/samba/source3/script/tests/test_symlink_rename_smb1_posix.sh

## Purpose
This test checks SMB1 POSIX rename semantics when the target path is an existing symlink. All attempted renames from a real file to symlink targets should fail with `NT_STATUS_OBJECT_NAME_COLLISION`.

## Important APIs, Functions, and Control Flow
The script builds local files, directories, missing targets, and no-permission targets both outside and inside the share. `do_cleanup` removes fixtures and restores permissions. `smbclient_expect_error` writes a command file with `posix`, the requested command, and `quit`, then runs `smbclient //$SERVER/local_symlinks -mNT1` and greps for the expected status. `test_symlink_rename_SMB1_posix` iterates rename cases for symlinks to nonexistent, outside-share, no-permission, and inside no-permission objects.

## State, Dependencies, Integration, and Risks
State includes share-local symlinks and `/tmp/symlink_rename_*.$$` outside-share fixtures. It depends on SMB1 POSIX extensions, Unix symlinks, and permission behavior. Risks include use of `/tmp` rather than `$TMPDIR` and permission cleanup requirements for chmod 0 directories. Test signals are exact `NT_STATUS_OBJECT_NAME_COLLISION` matches.
