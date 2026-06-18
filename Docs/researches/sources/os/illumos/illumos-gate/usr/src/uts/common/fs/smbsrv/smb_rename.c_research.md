# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_rename.c

## Purpose

`smb_rename.c` implements legacy SMB1 rename, NT rename, hard-link creation via NT rename information level, and a no-op NT transact rename compatibility handler.

## Main Interfaces

- `smb_pre_rename()`, `smb_post_rename()`, and `smb_com_rename()` handle `SMB_COM_RENAME`.
- `smb_pre_nt_rename()`, `smb_post_nt_rename()`, and `smb_com_nt_rename()` handle `SMB_COM_NT_RENAME`.
- `smb_nt_transact_rename()` validates a handle for NT transact rename and returns success without renaming, matching Windows behavior.

## Behavior And Data Flow

Legacy rename decodes source search attributes and source/destination paths, requires a disk tree, initializes and validates both pathnames, then delegates to `smb_common_rename()`. Wildcard rename is documented but not supported here.

NT rename decodes search attributes, information level, cluster count, and paths. It rejects non-disk trees, validates paths, rejects wildcard source paths with `NT_STATUS_OBJECT_PATH_SYNTAX_BAD`, then dispatches by information level: hard link uses `smb_make_link()`, rename/move use `smb_common_rename()`, move-cluster returns invalid parameter, and unknown levels return access denied.

NT transact rename only decodes a FID, validates that it exists, releases it, and returns success. The comment states this mirrors Windows servers, which do not rename in this path.

## Dependencies

This file depends on SMB path parsing/validation, common rename and hard-link filesystem helpers, FID lookup/release, tree type checks, request decode/encode, DTrace probes, and SMB error mapping.

## Notable Invariants And Risks

- Rename commands are valid only on disk trees.
- Path validation occurs before common filesystem operations.
- NT rename disallows wildcard source paths explicitly.
- Actual rename collision, delete-pending, share-mode, link, and filesystem semantics live in `smb_common_rename()` and `smb_make_link()`, not this adapter file.
