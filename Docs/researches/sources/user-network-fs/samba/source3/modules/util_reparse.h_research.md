<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.h -->
# sources/user-network-fs/samba/source3/modules/util_reparse.h

## Purpose
This header declares the reparse-point FSCTL helper API implemented by `util_reparse.c`. It exposes a small boundary used by SMB server code and VFS modules without leaking implementation details about xattrs or special-file synthesis.

## Important APIs, Types, And Functions
The declared APIs are `fsctl_get_reparse_point`, `fsctl_get_reparse_tag`, `fsctl_set_reparse_point`, and `fsctl_del_reparse_point`. All operate on `struct files_struct *fsp`; get returns a tag, talloc-owned output bytes, and output length; set/delete consume raw reparse buffer bytes and lengths.

## Control Flow
The header itself has no runtime flow. It establishes the contract that callers pass a memory context for returned or temporary allocations and receive `NTSTATUS` results.

## State And Persistence
No state is stored in the header. The declared functions persist or remove reparse data through the implementation's xattr and DOS attribute paths.

## Dependencies And Integration Points
It relies on Samba core types such as `NTSTATUS`, `TALLOC_CTX`, and `files_struct` being visible to includers. It integrates the FSCTL dispatch layer with the reparse utility implementation.

## Risks
Callers must respect ownership of returned `uint8_t *` buffers and must pass correctly sized Windows reparse buffers to set/delete. The header does not document those ownership and validation constraints beyond the function signatures.

## Test Signals
Compile coverage through any user of the FSCTL helpers confirms declaration compatibility. Behavioral signals come from `util_reparse.c` tests or SMB FSCTL integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.h -->
