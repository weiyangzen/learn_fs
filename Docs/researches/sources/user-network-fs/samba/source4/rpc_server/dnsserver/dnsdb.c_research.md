# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsdb.c

Purpose: AD/LDB persistence layer for the DNS RPC server. It enumerates DNS partitions and zones, reads partition metadata, and mutates `dnsZone`/`dnsNode` objects and `dnsRecord`/`dNSProperty` attributes.

Important APIs and control flow: `dnsserver_db_enumerate_partitions()` constructs the fixed DomainDnsZones and ForestDnsZones partitions. `dnsserver_db_enumerate_zones()` searches `CN=MicrosoftDNS` for `dnsZone` objects, maps `RootDNSServers` to `.`, ignores trust anchors, and parses zone properties. `dnsserver_db_partition_info()` reports replica state and cross-reference DN. Mutating record helpers increment SOA serials via `dnsserver_update_soa()`, convert RPC records to DNSP blobs, assign rank, search for existing nodes, and add/replace/delete `dnsRecord` values. Deleting the last record deletes the node. Zone property reset rewrites matching `dNSProperty` blobs. Zone creation builds a security descriptor using DnsAdmins SID, creates `dnsZone` properties, and adds an `@` node with SOA and NS records. Zone deletion performs a transaction and tree delete.

State and persistence: this file owns persistent writes to samdb through `ldb_add`, `ldb_modify`, `ldb_delete`, `dsdb_delete`, and transactions. It also mutates in-memory `zoneinfo` during property reset.

Dependencies and integration: used by the RPC DNS dispatch layer. Depends on SAMDB, DSDB utilities, generated DNSP/security NDR, SDDL decode, domain SID lookup, and loadparm DNS domain.

Risks and test signals: SOA serial handling and duplicate detection are central. Tests should cover permissions, tombstoned node resurrection, duplicate records, SOA update failures, TTL-only updates, property parsing with malformed short properties, primary-only zone creation, security descriptor creation, and transaction rollback on zone delete failure.
