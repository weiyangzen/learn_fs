# sources/user-network-fs/samba/source3/smbd/smb1_trans2.h

## Purpose

`smb1_trans2.h` is the small public interface for the SMB1 Transaction2 implementation. It exposes the two SMB1 command handlers implemented in `smb1_trans2.c` so the SMB1 server dispatch layer can route primary and secondary Transaction2 commands.

## Important APIs, Types, and Functions

- `void reply_trans2(struct smb_request *req)`: handles primary `SMBtrans2` requests, including full requests and first fragments of multi-packet transactions.
- `void reply_transs2(struct smb_request *req)`: handles `SMBtranss2` secondary fragments for pending SMB1 Transaction2 requests.

The header intentionally declares no local structs or constants. The request type comes from the included smbd/server headers used by compilation units that include this file.

## Control Flow

The file has no control flow of its own. Its declarations bind the SMB command dispatch table to the concrete implementation in `smb1_trans2.c`.

## State and Persistence Behavior

No state is defined in the header. Runtime state is held by the implementation through `struct smb_request`, `connection_struct`, pending transaction lists, directory pointers, and VFS/file structures.

## Dependencies and Integration Points

This header depends on the surrounding smbd type environment for `struct smb_request`. It is consumed by SMB1 dispatch code that needs to call the Transaction2 handlers without knowing their internal helper functions.

## Risks and Edge Cases

The main risk is API drift: changing either prototype must be synchronized with the SMB1 command dispatch and the definitions in `smb1_trans2.c`. Because these functions own packet replies and memory cleanup, callers must treat them as terminal request handlers.

## Test Signals

Build coverage is the primary signal for this header. Runtime signals come indirectly from SMB1 Transaction2 command tests that prove the dispatch layer still reaches `reply_trans2` and `reply_transs2`.
