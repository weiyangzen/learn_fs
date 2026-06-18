# sources/user-network-fs/samba/source3/libsmb/clitrans.c

## Purpose

This file is the common SMB1 transaction wrapper for libsmb client code. It provides async and sync entry points around `smb1cli_trans_send/recv`, including cancellation, output ownership transfer, minimum response validation, and optional DOS error mapping.

## Important APIs, Types, and Functions

The exported APIs are `cli_trans_send()`, `cli_trans_recv()`, and synchronous `cli_trans()`. `cli_trans_state` stores the `cli_state`, lower-level subrequest, receive flags, setup words, parameter bytes, data bytes, and their counts.

## Control Flow

`cli_trans_send()` creates a tevent request and calls `smb1cli_trans_send()` with the connection, timeout, pid, tree connect, session, pipe name/fid/function/flags, and caller-supplied setup/parameter/data buffers. Completion calls `smb1cli_trans_recv()` and stores returned buffers. `cli_trans_recv()` checks minimum setup/param/data sizes, talloc-moves requested buffers to the caller, and maps DOS statuses to NTSTATUS when `cli->map_dos_errors` is enabled. The sync wrapper rejects concurrent async calls and polls a private tevent context.

## State and Persistence Behavior

This wrapper does not define protocol semantics itself; side effects depend on the specific transaction command supplied by callers. It owns returned buffers until recv moves them. Cancellation forwards to the lower subrequest.

## Dependencies and Integration Points

It is used by many SMB1 helpers in this subset: FS info, listing, RAP, quota, print, and security descriptor code. It depends on `smb1cli_trans_*`, tevent NTSTATUS helpers, and `smbXcli_conn_has_async_calls()`.

## Risks and Test Signals

Risks include callers specifying wrong minimum lengths, DOS-to-NT mapping changing expected statuses, missing recv calls leaking buffers until request free, and sync misuse during active async work. Tests should cover minimum-length failures, buffer ownership moves, cancellation propagation, DOS error mapping on/off, transaction errors, and sync wrapper invalid-parameter behavior.
