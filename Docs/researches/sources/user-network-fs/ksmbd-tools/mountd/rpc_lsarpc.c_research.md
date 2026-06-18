<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c

## Purpose

Implements the LSARPC DCE/RPC service for policy handles, domain information, SID lookup, and name lookup.

## Important APIs, Types, and Functions

Important functions include policy-handle table alloc/lookup/free, `lsarpc_get_primary_domain_info_*`, `lsarpc_open_policy2_return`, `lsarpc_query_info_policy_*`, `lsarpc_lookup_sid2_*`, `lsarpc_lookup_names3_*`, `lsarpc_close_*`, public read/write entry points, and init/destroy.

## Control Flow

Initialization caches an uppercase hostname-derived domain name and creates the policy-handle table. The write phase parses opnum-specific handles, levels, SID arrays, or names. The read phase validates handles, writes domain role/account-domain responses, maps SIDs to names and names to domain SIDs/users, appends RPC return status, and writes DCE/RPC headers.

## State and Persistence Behavior

State includes global `ph_table`, `domain_name`, per-request `lsarpc_names_info` entries in the pipe, and handles embedded in `dce->lr_req`. Lookup entries are freed by the pipe entry callback.

## Dependencies and Integration Points

Depends on management/user, smbacl SID helpers, generic RPC/NDR helpers, passwd lookup by uid, GLib tables/strings, and global domain subauth config.

## Risks and Edge Cases

The switch cases use `case A || B`, which evaluates as a constant expression rather than two case labels; behavior relies on frag_length to distinguish close versus primary-domain info and deserves scrutiny. Binary handles are stored with string hash/equality, a potential mismatch for embedded NULs. Name parsing mutates strings with `strtok`.

## Test Signals

Tests should cover open/query/close policy, primary-domain info, lookup SID for known and unknown users, lookup names with domain prefixes, bad handles, malformed arrays, and the opnum 0/close ambiguity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c -->
