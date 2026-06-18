# sources/user-network-fs/samba/source3/smbd/smb1_utils.h

## Purpose

`smb1_utils.h` declares utility functions valid in the SMB1 server. It provides shared prototypes for legacy open fallback, keepalive sending, SMB output string appending, SMB1 search-path conversion, and FID-to-FSP lookup.

## Important APIs, Types, and Functions

- `fcb_or_dos_open`: legacy sharing-violation fallback for DOS/FCB deny modes.
- `send_keepalive`: RFC1002 keepalive packet sender.
- `message_push_string`: encoded string append helper for SMB response buffers.
- `filename_convert_smb1_search_path`: converts a search path while preserving the terminal wildcard mask separately.
- `file_fsp`: resolves a 16-bit SMB1 FID from an SMB request.

The header includes `includes.h`, `vfs.h`, `proto.h`, and string wrapper definitions, so consumers inherit Samba core types such as `NTSTATUS`, `TALLOC_CTX`, `connection_struct`, `files_struct`, and `smb_filename`.

## Control Flow

The header has no executable control flow. It establishes the cross-file contract consumed by SMB1 command handlers such as Transaction2, NT create, search, and related reply code.

## State and Persistence Behavior

No state is declared here. The declared functions can mutate request caches, file-handle references, caller-owned buffers, and mutable input paths in their implementation.

## Dependencies and Integration Points

This header is part of the smbd internal API. It connects SMB1-specific code to common VFS and string conversion types while keeping implementation details in `smb1_utils.c`.

## Risks and Edge Cases

Because these helpers have side effects that are not visible from prototypes alone, call sites need to know ownership rules: `message_push_string` may replace the buffer pointer, `filename_convert_smb1_search_path` edits the path string, `file_fsp` may cache `chain_fsp`, and `fcb_or_dos_open` returns a new FSP sharing an underlying handle.

## Test Signals

Build checks catch prototype drift. Functional coverage comes from SMB1 tests that exercise each declared helper through command handlers.
