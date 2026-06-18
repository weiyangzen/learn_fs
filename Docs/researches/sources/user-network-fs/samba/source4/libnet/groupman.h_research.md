<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.h -->
# sources/user-network-fs/samba/source4/libnet/groupman.h

Purpose: declares the libnet SAMR group-add request structure.

Important APIs and types: `struct libnet_rpc_groupadd`, with input `domain_handle` and `groupname`, and output `group_handle`.

Control flow: no executable flow. The implementation uses the domain handle and group name to create a SAMR domain group.

State and persistence: the output handle represents server-side state opened by group creation. The caller is responsible for later closure through SAMR mechanisms.

Risks: the header does not expose the created RID even though implementation records it, limiting caller verification without extra lookups. Test signals include consumers closing the returned handle and compile coverage for group management functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.h -->
