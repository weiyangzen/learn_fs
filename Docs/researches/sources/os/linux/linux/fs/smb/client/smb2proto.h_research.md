# File Research: sources/os/linux/linux/fs/smb/client/smb2proto.h

## Purpose

`smb2proto.h` is the primary exported prototype header for the CIFS SMB2/SMB3 client implementation. It declares error mapping, PDU validation, signing, request setup, reconnect, path operations, core SMB2 command workers, and helper parsers used across the SMB client.

## Main API Areas

- Error and message handling: `map_smb2_to_linux_error()`, `smb2_check_message()`, `smb2_calc_size()`, `smb2_get_data_area_len()`.
- Path conversion and path-level operations: UTF-16 conversion, query path info, mkdir/rmdir/unlink/rename/hardlink/symlink helpers, file size setting, reparse point handling.
- Signing and transport setup: `smb2_verify_signature()`, `smb2_check_receive()`, `smb2_setup_request()`, `smb2_setup_async_request()`.
- Session/tcon lookup and reconnect: `smb2_find_smb_tcon()`, `smb2_reconnect_server()`, replay helpers.
- Core SMB2 command workers: negotiate, session setup, logoff, tree connect/disconnect, open, ioctl, notify, close, flush, query info, read/write, echo, query directory, set info, set EOF/ACL/EA/compression, oplock and lease break, filesystem info, lock.
- Request init/free helpers for open, ioctl, close, flush, query info, query directory, and set info.
- Validation and parsing helpers: create-context parsing, iov validation/copy, filesystem stat copy, POSIX info parsing, SID sizing.
- SMB3 crypto: `smb3_crypto_aead_allocate()` and preauth update.

## Integration

- Includes `cached_dir.h` because several higher-level path operations interact with cached directory state.
- Used by SMB2 PDU construction (`smb2pdu.c`), transport signing (`smb2transport.c`), reconnect paths, inode/path helpers, and operation tables.
- Provides the public surface that dialect operation tables can bind to.

## Risk Notes

- This header exposes a broad internal API; signature changes can have a large blast radius across the CIFS client.
- Several APIs transfer buffer ownership through `struct kvec`, `char **`, and `int *buftype`; callers must follow the documented/freeing conventions in the implementation.
- The header mixes high-level VFS path helpers and low-level PDU helpers, so include dependencies should be changed cautiously.
