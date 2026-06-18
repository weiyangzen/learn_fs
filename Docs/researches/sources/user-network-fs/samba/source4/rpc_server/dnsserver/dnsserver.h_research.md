# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsserver.h

Purpose: shared internal header for the Samba DNS RPC server.

Important APIs/types: defines `dnsserver_serverinfo`, `dnsserver_zoneinfo`, `dnsserver_partition`, `dnsserver_partition_info`, `dnsserver_zone`, and `dns_tree`. Declares data conversion functions from `dnsdata.c`, server/zone utility functions from `dnsutils.c`, and database functions from `dnsdb.c`.

State and persistence: structs represent per-connection server state, AD DNS partitions/zones, temporary parsed zone properties, and enumeration trees. Persistence itself is through declared `dnsserver_db_*` functions.

Dependencies and integration: includes generated DNSP/DNSServer IDL types, loadparm, and LDB. It is the coupling point among DNS RPC dispatch, data conversion, utility initialization, and database mutation.

Risks and test signals: changes to struct layout or prototypes affect all DNS server files. Compile and ABI checks should cover all consumers; behavioral tests should confirm `zoneinfo` defaults and DB helper contracts remain aligned.
