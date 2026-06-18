# sources/user-network-fs/samba/source4/dsdb/repl/drepl_partitions.c

Purpose: loads and refreshes DREPL partition/source topology and constructs reusable outgoing connections to source DSAs.

Important APIs/functions: `dreplsrv_load_partitions()` reads this NTDS Settings object's NC attributes; `dreplsrv_refresh_partitions()` reloads NC metadata, UDV, `repsFrom`, and `repsTo`; `dreplsrv_partition_find_for_nc()`, `_source_dsa_by_guid()`, `_source_dsa_by_dns()`, and `_source_dsa_temporary()` resolve replication targets; `dreplsrv_out_connection_attach()` caches DRSUAPI bindings; `dreplsrv_get_target_principal()` chooses Kerberos target SPNs.

Control flow/state: startup loads master/full/partial replica NCs, deduplicates partitions, then refreshes each partition. Refresh fills `partition->nc`, UDV, `sources` from `repsFrom`, and `notifies` from `repsTo` entries not already in sources. Parsed reps blobs become long-lived in-memory `dreplsrv_partition_source_dsa` entries attached to cached connections. The actual durable state remains in DSDB attributes.

Dependencies/integration: SAMDB reference searches, extended DNs, DRSUAPI reps blob NDR, dcerpc binding parser, Kerberos SPN validation, partial replica flags, and DREPL service state. Risks include silently tolerating absent remote server metadata, target-principal fallback complexity, never removing old source structs except updating/reusing matches, and temporary DSA use for first replication. Test signals: partition dedupe, RODC/partial flags, reps blob parse failures, target principal selection with/without `dNSHostName`, and refresh after KCC topology changes.
