<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.h -->
# sources/user-network-fs/samba/source4/libnet/groupinfo.h

Purpose: declares the input/output contract and monitor payload structures for libnet SAMR group information queries.

Important APIs and types: `struct libnet_rpc_groupinfo` with input `domain_handle`, `groupname`, `sid`, and `level`, and output `union samr_GroupInfo info`; monitor payloads `msg_rpc_open_group`, `msg_rpc_query_group`, and `msg_rpc_close_group`.

Control flow: no executable flow. The struct supports two selection modes, SID or group name, with the implementation choosing SID if present.

State and persistence: no state in the header. Output mirrors the SAMR query level selected by the caller.

Risks: no explicit discriminator identifies which field of `union samr_GroupInfo` is valid, so callers must track the requested level. SID and groupname are both nullable by type, but implementation requires at least one meaningful identifier. Test signals include compile coverage for all query levels and monitor payload consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.h -->
