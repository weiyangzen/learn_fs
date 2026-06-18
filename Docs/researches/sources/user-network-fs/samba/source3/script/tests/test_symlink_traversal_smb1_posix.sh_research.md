# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1_posix.sh

## Purpose
This companion to the SMB1 traversal test verifies SMB1 POSIX-specific symlink behavior, especially that symlinks can be listed/stat'ed and wildcard `*` is treated as a valid path component rather than only a search pattern.

## Important APIs, Functions, and Control Flow
The setup and cleanup matrix mirrors `test_symlink_traversal_smb1.sh`. `smbclient_expect_error` adds `posix` before each command and forces `-mNT1`. `test_symlink_traversal_SMB1_posix_onename` validates `get`, `ls`, `stat`, `del`, and optional rename behavior for each symlink category with POSIX-specific expected statuses. The main test covers nonexistent, outside-share, no-permission, and inside-share no-permission paths.

## State, Dependencies, Integration, and Risks
State is local symlink and permission fixtures under the share plus temporary outside targets. It depends on SMB1 POSIX extensions being enabled and `smbclient` POSIX command mode. Risks include differences between POSIX and non-POSIX error mappings causing brittle expectations, and fixture cleanup requiring permission restoration. Signals are exact status checks including `NT_STATUS_OK` for list/stat paths.
