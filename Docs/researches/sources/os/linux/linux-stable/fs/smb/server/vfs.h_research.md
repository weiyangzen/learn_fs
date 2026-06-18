# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs.h

## Summary
Declares ksmbd’s VFS helper API, stream types, create-option constants, directory enumeration state, and kstat wrapper used by SMB directory/stat responses.

## Main Responsibilities
- Define data and directory stream type constants.
- Define ksmbd-only create option flags and SMB create-option values.
- Define `struct ksmbd_dir_info`, `struct ksmbd_readdir_data`, and `struct ksmbd_kstat`.
- Declare path lookup, create, I/O, metadata, xattr, security descriptor, DOS attribute, copychunk, sparse range, lock, and POSIX ACL helpers.

## Cross-File Interactions
Used by SMB2 command handlers, directory enumeration, ACL code, file cache code, and xattr/metadata handling.

## Risks
The declarations here are a wide internal VFS contract. Changes to ownership, buffer, or path-locking expectations require coordinated updates in SMB2 command handlers and cache/lifetime code.
