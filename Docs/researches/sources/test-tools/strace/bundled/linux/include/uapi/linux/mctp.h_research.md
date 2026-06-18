# sources/test-tools/strace/bundled/linux/include/uapi/linux/mctp.h

Purpose: defines the Management Component Transport Protocol socket ABI, address structures, tag flags, extended address option, and tag allocation ioctls.

Important APIs/types/functions: exports `mctp_eid_t`, `mctp_addr`, `sockaddr_mctp`, `sockaddr_mctp_ext`, `mctp_fq_addr`, network/address constants, tag flags (`MCTP_TAG_OWNER`, `MCTP_TAG_PREALLOC`), `MCTP_OPT_ADDR_EXT`, `SIOCMCTP*TAG*` ioctls, and `mctp_ioc_tag_ctl`/`mctp_ioc_tag_ctl2`.

Control flow: userspace binds/connects/sends with MCTP sockaddr forms, optionally requests extended hardware address data, allocates preallocated tags for a peer, sends traffic, then drops tags.

State/persistence behavior: allocated tags are kernel state associated with socket/peer/network until explicitly dropped or socket cleanup. Addressing is scoped by local MCTP network IDs and EIDs.

Dependencies/integration: depends on Linux socket and netdevice definitions, especially `MAX_ADDR_LEN`. Integrates with AF_MCTP sockets, network-device binding, and platform management controllers.

Risks and test signals: deprecated TAG ioctls lack network ID and can be wrong on multi-network systems. Tests should cover sockaddr decoding, extended address option, tag flags, TAG2 structs, and `MCTP_ADDR_ANY`/`NULL`.
