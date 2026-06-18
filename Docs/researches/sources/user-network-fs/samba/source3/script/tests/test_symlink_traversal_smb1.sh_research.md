# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1.sh

## Purpose
This test validates SMB1 non-POSIX error mappings when traversing, listing, deleting, or renaming through symlinks to nonexistent, outside-share, and no-permission targets.

## Important APIs, Functions, and Control Flow
It creates a matrix of symlinks in the share root and under `emptydir`, plus no-permission file/directory objects inside the share. `smbclient_expect_error` runs a generated command file against `//$SERVER/local_symlinks -mNT1` and checks either absence of `NT_STATUS_` for `NT_STATUS_OK` or presence of an expected error. `test_symlink_traversal_SMB1_onename` applies `get`, `ls`, `del`, and optional `rename` checks for one symlink name. `test_symlink_traversal_SMB1` calls it for multiple symlink categories and then checks no-permission direct and symlinked paths.

## State, Dependencies, Integration, and Risks
State is the generated filesystem matrix under `$LOCAL_PATH` and outside fixtures under `${TMPDIR:-/tmp}`. It depends on `follow symlinks` behavior for the `local_symlinks` share and SMB1 wildcard semantics. Risks are exact error-code coupling and chmod cleanup on no-permission directories. Signals are many precise `NT_STATUS_*` assertions.
