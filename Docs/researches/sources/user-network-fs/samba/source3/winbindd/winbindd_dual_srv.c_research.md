# sources/user-network-fs/samba/source3/winbindd/winbindd_dual_srv.c

## Purpose
Implements the in-child server side of the wbint/winbind internal RPC interfaces. It exposes SID/name lookup, idmap translation/allocation, NSS info, token/group queries, DC locator, trust account operations, netlogon/LSA forwarding helpers, forest trust maintenance, trusted-domain listing, and name normalization to the parent and IRPC frontends.

## Important APIs, Types, And Control Flow
Simple wbint calls include `_wbint_Ping`, `_wbint_InitConnection`, `_wbint_LookupSid`, `_wbint_LookupName`, `_wbint_LookupSids`, group/alias/member queries, sequence number, `DsGetDcName`, and normalization map/unmap. Idmap calls translate between domain RID batches and Unix IDs via idmap domain methods, allocate UIDs/GIDs, and enforce configured id ranges. Trust/netlogon calls include `_wbint_CheckMachineAccount`, `_wbint_ChangeMachineAccount`, `_wbint_PingDc`, `_winbind_DsrUpdateReadOnlyServerDnsRecords`, `_winbind_SamLogon`, `_winbind_LogonControl`, `_winbind_GetForestTrustInformation`, and `_winbind_SendToSam`. Many network operations call `reset_cm_connection_on_error()` and retry once after invalidating connection state.

## State And Persistence
Mutates the child domain's `dcname`, `force_dc`, initialized flags, connection manager state, and netlogon reauth flags. Trust password changes and forest trust updates persist via passdb/secrets or local LSA RPCs. Cache-backed lookup calls read/write through `wb_cache_*` layers outside this file.

## Dependencies And Integration Points
Integrates with `wb_child_domain()`, idmap backend APIs, winbind cache, netlogon credential client, connection manager, passdb, local LSA, DSDB forest trust helpers, generated NDR scompat server code, and Samba RPC client/server infrastructure.

## Risks And Test Signals
Risks include inconsistent NTSTATUS/WERROR layering, partial idmap mappings, trust-password races, forest-trust update side effects, retry loops that hide connection churn, and operations that require the child to have a valid domain. Test with remote and internal domains, unmapped IDs, out-of-range idmap results, DC disconnect/reconnect, expired trust passwords, RODC DNS update, SamLogon validation levels 3/6, LogonControl modes, forest-trust update flags, and name normalization round-trips.
