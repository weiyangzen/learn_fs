<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c

## Purpose

Implements the WKSSVC NetWkstaGetInfo DCE/RPC service.

## Important APIs, Types, and Functions

Important functions are `wkssvc_parse_netwksta_info_req`, `wkssvc_netwksta_info_invoke`, `wkssvc_netwksta_info_return`, level-100 representation/data callbacks, and public read/write request entry points.

## Control Flow

The write phase parses a unique server-name string and requested info level. The read phase supports level 100 only, writing NT platform id, server name, workgroup/domain name, version major/minor, return status, and DCE/RPC headers.

## State and Persistence Behavior

State is one decoded `wi_req` in the DCE context. Server-name memory is freed after response serialization.

## Dependencies and Integration Points

Depends on generic RPC helpers, global `work_group`, tools charset conversion, and restricted-context logic.

## Risks and Edge Cases

Only level 100 is implemented. The server-name echo behavior is minimal. Unsupported levels must return invalid-level without leaking parsed strings.

## Test Signals

Tests should request level 100 with normal and empty server names, unsupported levels, restricted context, and malformed string payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c -->
