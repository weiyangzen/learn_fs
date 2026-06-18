# sources/user-network-fs/samba/source3/libsmb/clisymlink.c

## Purpose

This file implements client symlink and reparse-point handling. It can create Windows symlink reparse points, fetch raw reparse data, and read links either through SMB1 POSIX extensions or through `FSCTL_GET_REPARSE_POINT`.

## Important APIs, Types, and Functions

Important APIs are `cli_create_reparse_point_send/recv`, `cli_symlink_send/recv`, `cli_symlink()`, `cli_get_reparse_data_send/recv`, `cli_get_reparse_data()`, `cli_readlink_send/recv`, and `cli_readlink()`. State structs track fnums, pending FSCTL status, reparse blobs, returned raw data, POSIX targets, and event/CLI pointers.

## Control Flow

Creating a reparse point opens the new file with `FILE_OPEN_REPARSE_POINT`, `FILE_CREATE`, and Windows-like symlink creation access masks, sends `FSCTL_SET_REPARSE_POINT`, then closes. If setting the reparse point fails, it marks the file delete-on-close before closing. `cli_symlink_send()` marshals an `IO_REPARSE_TAG_SYMLINK` buffer and delegates to create-reparse. Fetching reparse data opens the path with read attributes/EA and `FILE_OPEN_REPARSE_POINT`, calls `cli_fsctl_send(FSCTL_GET_REPARSE_POINT)`, then closes before completing. `cli_readlink_send()` prefers negotiated SMB1 POSIX readlink when available; otherwise it fetches and parses symlink reparse data.

## State and Persistence Behavior

Symlink creation persists a new remote file with reparse metadata. Failed create attempts try to clean up with delete-on-close. Raw reparse data and parsed names are talloc-moved to callers. No local durable state exists.

## Dependencies and Integration Points

The file depends on create/close/delete-on-close helpers, `cli_fsctl`, POSIX readlink helpers, reparse marshalling/parsing, security access constants, and SMB2 impersonation values. `clirap.c` uses `cli_get_reparse_data_send()` to classify reparse-point modes.

## Risks and Test Signals

Risks include cleanup failure after partial symlink creation, parsing non-symlink reparse tags as readlink, server-specific access/share requirements, and close-status masking of FSCTL errors. Tests should cover successful symlink creation, FSCTL failure cleanup, readlink via SMB1 POSIX and reparse paths, non-symlink reparse data, malformed reparse buffers, relative/absolute symlink flags, and close failure precedence.
