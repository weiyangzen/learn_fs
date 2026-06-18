# sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.c

Purpose: implements DNS aging maintenance for AD-integrated zones. It tombstones expired `dnsRecord` values and later deletes tombstoned `dnsNode` objects after the configured tombstone interval.

Important APIs/functions: `dns_tombstone_records()` iterates zones and calls `dns_tombstone_records_zone()`; `dns_delete_tombstones()` removes aged tombstoned nodes; `copy_current_records()` copies only non-expired records. Tombstoning uses `dnsp_DnssrvRpcRecord` NDR decoding/encoding and writes a `DNS_TYPE_TOMBSTONE` record plus `dNSTombstoned=TRUE` when all live records expire.

Control flow/state: zone scavenging reads zone properties (`dwNoRefreshInterval`, `dwRefreshInterval`), computes the cutoff from the current DNS timestamp, searches with `DSDB_MATCH_FOR_DNS_TO_TOMBSTONE_TIME`, and modifies each node. Updates are constrained by leaving the old `dnsRecord` element as `MOD_DELETE` and adding a replacement element, so concurrent record changes fail instead of being overwritten. Deletion searches tombstoned nodes, validates the single tombstone record, handles older Samba tombstone time encoding, and deletes via `dsdb_delete()`.

Dependencies/integration: DNS server common zone discovery/properties, LDB custom matching rules, NDR DNS record formats, loadparm `dnsserver:dns_tombstone_interval`, DSDB delete/modify helpers, and KCC periodic/Python admin bindings. Risks include large tombstone searches, malformed DNS blobs, races causing modify failure, and time conversion edge cases. Test signals: zones without property sets are skipped, mixed live/expired multi-value nodes retain live records, all-expired nodes become tombstoned, and old-hour-format tombstones are tolerated.
