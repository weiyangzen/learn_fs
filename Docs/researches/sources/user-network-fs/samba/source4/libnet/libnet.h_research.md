<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.h -->
# sources/user-network-fs/samba/source4/libnet/libnet.h

Purpose: defines the central source4 libnet context and aggregates libnet operation headers.

Important APIs and types: `struct libnet_context`, including credentials, SAMR connection state, LSA connection state, `resolve_context`, `tevent_context`, `loadparm_context`, and optional `server_address`. It includes operation headers for composite monitoring, user/group management, password, time, RPC, join, site, DC promotion/demotion, samsync, vampire, share, lookup, domain, and generated prototypes.

Control flow: no executable flow. The context layout defines how libnet operations share credentials, already-open pipes, binding handles, domain metadata, policy handles, and runtime contexts.

State and persistence: this is the shared mutable state for libnet clients. SAMR and LSA substructures cache pipes, binding handles, names, SIDs, access masks, and policy handles across operations.

Risks: operations sharing one context must coordinate cached handles and server address overrides. Header aggregation can create broad compile dependencies and hidden coupling. Test signals include initialization defaults, multiple operations sharing SAMR/LSA handles, and consumers compiling with all included headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.h -->
