<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.c -->
# sources/user-network-fs/samba/source4/libnet/groupman.c

Purpose: implements a composite SAMR group creation helper.

Important APIs and types: `struct groupadd_state`, `libnet_rpc_groupadd_send`, `libnet_rpc_groupadd_recv`, `libnet_rpc_groupadd`, and `continue_groupadd_created`. It uses `samr_CreateDomainGroup` over a supplied DCERPC binding handle and domain policy handle.

Control flow: `send` validates the binding and io, creates a composite context, copies the domain handle, allocates an LSA string for the requested group name, sets access mask to zero, points outputs at state-owned `group_handle` and `group_rid`, then sends `dcerpc_samr_CreateDomainGroup_r_send`. The continuation receives transport status, checks `creategroup.out.result`, and completes. `recv` copies the returned group handle into `io->out`.

State and persistence: successful execution persists a new domain group on the remote SAM database and returns an open group policy handle. The returned RID is tracked internally but not exposed by the header.

Risks: access mask zero may depend on server defaults and may not grant useful handle permissions. The monitor function is stored but not used, so callers expecting progress events receive none. Test signals include duplicate group errors, permission failures, returned handle usability, and memory failure during LSA string construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.c -->
