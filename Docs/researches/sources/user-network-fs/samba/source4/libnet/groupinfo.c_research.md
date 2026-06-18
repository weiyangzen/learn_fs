<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.c -->
# sources/user-network-fs/samba/source4/libnet/groupinfo.c

Purpose: implements an async composite SAMR flow for querying group information by group SID or group name.

Important APIs and types: `struct groupinfo_state`, `libnet_rpc_groupinfo_send`, `libnet_rpc_groupinfo_recv`, `libnet_rpc_groupinfo`, and continuation callbacks for lookup, open group, query group info, and close group. It depends on `dcerpc_samr_*_r_send/recv`, SAMR NDR types, policy handles, and libnet monitor messages.

Control flow: `send` validates binding and io. If `io->in.sid` is supplied, it parses the SID and uses the final subauthority as the group RID, then opens the group. Otherwise it calls `samr_LookupNames` for one group name, validates RID/type counts, then opens the group. After open it queries `samr_QueryGroupInfo` at the requested level, steals the returned info union, closes the group handle, and completes. Each major stage can emit a monitor message.

State and persistence: remote state is read-only except opening/closing handles. Output `union samr_GroupInfo` is stolen into caller memory in recv and copied into `io->out.info`.

Risks: SID parsing only uses the last subauthority as RID and does not verify domain SID alignment with `domain_handle`. Monitor payload allocations are not checked uniformly after every field. Test signals include SID and name paths, missing group, invalid lookup response counts, query levels, close failure, and monitor callback contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.c -->
