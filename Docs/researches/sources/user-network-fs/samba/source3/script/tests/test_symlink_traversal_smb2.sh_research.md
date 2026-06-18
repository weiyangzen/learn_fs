# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb2.sh

## Purpose
This larger symlink traversal regression test verifies SMB2 behavior for symlink traversal, wildcard paths, path component error precedence, no-permission directories, and an attempted symlink escape toward `/etc/passwd`.

## Important APIs, Functions, and Control Flow
The setup creates root and `emptydir` fixtures: regular files, directories with subfiles/subdirs, symlinks to dot, files, dirs, nonexistent and outside-share targets, no-permission objects, and `x` pointing outside the share. `smbclient_expect_error` runs commands against `//$SERVER/local_symlinks` without forcing NT1. `test_symlink_traversal_SMB2_onename` covers `get`, `ls`, `del`, and rename cases for each symlink name. `test_symlink_traversal_SMB2` adds detailed checks for ordinary files/directories, symlinks to those objects, nonexisting multi-component paths, access-denied paths, and `get x/passwd`.

## State, Dependencies, Integration, and Risks
State is a broad local fixture tree and outside temporary targets. It depends on SMB2 symlink semantics, share configuration with `follow symlinks = yes`, and exact server-side path resolution precedence. The security-sensitive signal is `x/passwd` returning `NT_STATUS_OBJECT_PATH_NOT_FOUND`. Risks are high brittleness from many exact error strings and cleanup needing chmod restoration for denied directories.
