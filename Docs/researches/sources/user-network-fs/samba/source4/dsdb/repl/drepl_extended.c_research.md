# sources/user-network-fs/samba/source4/dsdb/repl/drepl_extended.c

Purpose: schedules DRS extended operations as specialized `DsGetNCChanges` pulls against a role owner or source DSA, used by FSMO transfer, RID allocation, and secret replication.

Important APIs/functions: `drepl_request_extended_op()` is the public scheduler. `drepl_create_extended_source_dsa()` creates a temporary `dreplsrv_partition_source_dsa` with a synthetic partition, source DSA GUID/DNS name, outgoing connection, UDV, high-watermark copied from known partition state when available, and writable flags when allowed. `extended_op_callback()` unlinks the temporary source and forwards completion to the caller's callback.

Control flow/state: callers pass NC DN, source DSA DN, extended operation code, `fsmo_info`, minimum USN, and callback data. The file builds enough in-memory partition/source state to reuse the normal pull queue, schedules `dreplsrv_schedule_partition_pull_source()`, and immediately runs pending operations. Persistent effects are performed later by the pull helper and remote FSMO/RID/secret semantics; this file itself only constructs transient state.

Dependencies/integration: SAMDB GUID/NC-root lookup, UDV loading, `samdb_ntds_msdcs_dns_name()`, outgoing connection attachment, and the central DREPL queue. Risks include temporary object lifetime, using `min_usn` only indirectly/not in the visible source setup, failure to find source GUIDs, and callback correctness. Test signals: role transfer/RID/secret paths should schedule and complete callbacks, preserve existing high-watermarks, and clean up temporary source references.
