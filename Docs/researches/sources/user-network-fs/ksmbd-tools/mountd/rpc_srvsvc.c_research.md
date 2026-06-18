<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c

## Purpose

Implements the SRVSVC DCE/RPC service for share enumeration and share information.

## Important APIs, Types, and Functions

Important functions include share type/entry size/representation/data callbacks, `srvsvc_parse_share_info_req`, `srvsvc_share_enum_all_invoke`, `srvsvc_share_get_info_invoke`, `srvsvc_share_info_return`, and public read/write request entry points.

## Control Flow

The write phase parses server name, level, request container, max size, resume handle, or share name. It collects browseable/available shares or a single allowed share, respecting host allow/deny maps and restricted context. The read phase chooses level 0 or 1 serializers, writes NDR union/container data, total entries, resume handle, return status, and DCE/RPC headers.

## State and Persistence Behavior

State is per-pipe share references held in `pipe->entries`, decoded request strings in `dce->si_req`, entry callbacks, and processed counters. Entries are released by `__share_entry_processed`.

## Dependencies and Integration Points

Depends on management/share reference APIs, generic RPC/NDR helpers, and kernel RPC status codes.

## Risks and Edge Cases

Only levels 0 and 1 are supported. Host filtering uses simple share maps. Buffer-size continuation must preserve pending entries and free request strings only when complete. Restricted context changes status from invalid parameter to access denied.

## Test Signals

Tests should enumerate with no shares, multiple browseable/unbrowseable shares, max-size constrained responses, get info for missing/denied/allowed shares, levels 0/1/unsupported, and restricted anonymous access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c -->
