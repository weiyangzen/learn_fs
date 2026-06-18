## sources/user-network-fs/libtirpc/src/netname.c

Purpose: Converts local Unix user/host identities into Secure RPC network names.

Important APIs and control flow: `getnetname` chooses `host2netname` for effective uid 0 and `user2netname` otherwise. `user2netname` obtains the default NIS/RPC domain if none is supplied, checks the formatted length against `MAXNETNAMELEN`, and writes `unix.<uid>@<domain>`. `host2netname` similarly defaults domain and hostname, then writes `unix.<host>@<domain>`.

State and persistence: No owned persistent state. It reads effective uid, hostname, and default domain state from system/RPC helpers.

Dependencies and integration: Complements `netnamer.c` reverse mapping and key/publickey lookup. Uses `__rpc_get_default_domain`.

Risks and test signals: Uses `sprintf` after manual length checks. Tests should cover root/user branch, explicit/default domain, default hostname, maximum name lengths, and domain lookup failure.
