<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h

## Purpose

Declares SRVSVC service entry points for share enumeration and share info RPCs.

## Important APIs, Types, and Functions

Exposes `rpc_srvsvc_read_request` and `rpc_srvsvc_write_request` over `ksmbd_rpc_pipe` and `ksmbd_rpc_command`.

## Control Flow

Generic RPC dispatch calls write to parse and collect share entries, then read to serialize DCE/RPC response data.

## State and Persistence Behavior

State is kept in the shared RPC pipe entries and decoded SRVSVC request in `ksmbd_dcerpc`.

## Dependencies and Integration Points

Depends on rpc.h and share management implementation.

## Risks and Edge Cases

Unsupported levels/opnums and restricted anonymous context must map to correct RPC status codes.

## Test Signals

Tests should enumerate shares at levels 0/1, get info for allowed/denied/missing shares, and enforce restricted context behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h -->
