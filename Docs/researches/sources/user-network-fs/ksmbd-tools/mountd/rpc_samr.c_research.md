<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c

## Purpose

Implements the SAMR DCE/RPC service for domain and user account queries used by Windows clients.

## Important APIs, Types, and Functions

Important functions include connect-handle table alloc/lookup/free, `samr_connect5_*`, enum/lookup/open domain, lookup/open user, query user info, query security, group/alias membership, close handlers, domain entry initialization, and public read/write entry points.

## Control Flow

Initialization creates uppercase hostname and Builtin domain entries plus the handle table. The write phase parses opnum-specific handles, names, RIDs, and access masks. The read phase validates handles/refcounts, resolves users through user management, writes NDR domain arrays, user RID/type arrays, large user-info level 0x15 structures, security descriptors via smbacl, group membership, alias membership, status, and DCE/RPC headers.

## State and Persistence Behavior

State includes global `ch_table`, `domain_entries`, `domain_name`, `num_domain_entries`, handle refcounts, and an optional user pointer stored in a connect handle after lookup-names. Responses use per-DCE decoded `sm_req` state.

## Dependencies and Integration Points

Depends on management/user, smbacl, generic RPC helpers, GLib, hostname, and global subauth config.

## Risks and Edge Cases

Handle/user lifetime across reloads is sensitive. `profile_path` allocation appears short for the added separator and `profile` suffix. Many NDR structures are hand-coded with fixed constants. Only a subset of SAMR is implemented.

## Test Signals

Tests should cover every supported opnum, bad handles, unknown users, refcounted close sequences, user info buffer layout, security descriptor generation, group membership constants, restricted context, and fuzzed short requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c -->
