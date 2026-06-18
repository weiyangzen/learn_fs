<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h

## Purpose

Declares LSARPC service support for domain/account lookup over DCE/RPC.

## Important APIs, Types, and Functions

Defines handle sizes, domain string size, `struct policy_handle`, `struct lsarpc_names_info`, read/write request handlers, and init/destroy lifecycle.

## Control Flow

rpc.c dispatches LSARPC write/read phases into this service. The implementation tracks policy handles and converts SIDs and account names into NDR responses.

## State and Persistence Behavior

State includes an LSARPC policy-handle table, per-request lookup entries, and a cached uppercase host-derived domain name.

## Dependencies and Integration Points

Depends on smbacl SID structures, user management, generic RPC helpers, and GLib tables.

## Risks and Edge Cases

Handle identity uses binary handles stored in GLib hash tables, so hash/equality semantics must match handle memory. SID/name mapping returns partial success for unmapped identities.

## Test Signals

Tests should open/query/close policies, lookup known and unknown SIDs/names, and verify handle cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h -->
