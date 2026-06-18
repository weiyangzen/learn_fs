<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.h -->
# sources/user-network-fs/samba/source3/torture/vfstest.h

## Purpose
`vfstest.h` declares the shared structures and command interface used by the VFS test harness and its command modules.

## Important APIs, types, and functions
- `struct func_entry` names a simple VFS function callback taking `struct connection_struct *` and a path.
- `struct vfs_state` carries harness state: connection, message id, open file table, current directory, and scratch data buffer.
- `vfstest_get_smbreq()` is declared for command modules that need a synthetic `struct smb_request`.
- `struct cmd_set` defines a command name, handler callback, description, and usage text.
- `cmd_test_chain()` is declared for the optional SMB1 chain parser command.

## Control flow
The header itself has no control flow. It defines the ABI between `vfstest.c`, `cmd_vfs.c`, and `vfstest_chain.c`: command tables expose `struct cmd_set` entries, and command handlers receive the same `vfs_state` and talloc context shape.

## State and persistence behavior
The main state contract is `struct vfs_state`. Ownership is shared by the harness: command modules may inspect and update `files`, `currentdir`, `data`, and `data_size`, while the harness owns allocation and teardown.

## Dependencies and integration points
The header relies on forward declarations from included Samba headers in users of the file: `connection_struct`, `files_struct`, `smb_Dir`, `smb_request`, `TALLOC_CTX`, and `NTSTATUS`. It is included by `vfstest.c`, `cmd_vfs.c`, and `vfstest_chain.c`.

## Risks and edge cases
- `files[1024]` is a fixed-size open-file registry; command modules must avoid unchecked indexes.
- `data` is an untyped scratch pointer, so producers and consumers must agree on representation.
- The header has no include guard in the excerpted file, so multiple inclusion safety depends on local include patterns.

## Test signals
Compile success of `vfstest` and optional SMB1 chain support is the primary signal. Runtime command tests validate that command handlers interpret `vfs_state` consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.h -->
