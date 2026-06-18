<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h

## Purpose

Declares WKSSVC workstation information service entry points.

## Important APIs, Types, and Functions

Exposes `rpc_wkssvc_read_request` and `rpc_wkssvc_write_request`.

## Control Flow

Generic RPC write parses NetWkstaGetInfo arguments; read serializes level 100 workstation info.

## State and Persistence Behavior

State lives in `ksmbd_dcerpc.wi_req` during one request.

## Dependencies and Integration Points

Depends on rpc.h and global workgroup/server configuration.

## Risks and Edge Cases

Only level 100 is implemented; other levels must return invalid-level errors.

## Test Signals

Tests should request level 100, unknown levels, restricted anonymous context, and malformed server-name strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h -->
