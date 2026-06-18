# sources/user-network-fs/samba/source4/ldap_server/ldap_backend.c

## Purpose

`ldap_backend.c` maps decoded LDAP operations onto Samba's LDB/SAM database backend. It initializes per-connection SAMDB handles, translates LDB errors, encodes and queues replies, and implements search, mutation, compare, abandon, and dispatch behavior.

## Important APIs, Types, and Functions

Public entry points are `ldapsrv_backend_Init()`, `ldapsrv_init_reply()`, `ldapsrv_queue_reply()`, and `ldapsrv_do_call()`. Major handlers include `ldapsrv_SearchRequest()`, `ldapsrv_ModifyRequest()`, `ldapsrv_AddRequest()`, `ldapsrv_DelRequest()`, `ldapsrv_ModifyDNRequest()`, `ldapsrv_CompareRequest()`, `ldapsrv_AbandonRequest()`, and `ldapsrv_expired()`.

## Control Flow

Backend init opens `sam.ldb`, records encrypted-connection state for TLS/SASL seal/LDAPI, and stores supported SASL mechanisms. Dispatch checks ticket expiry, critical controls, anonymous authorization logging, and LDAP message type. Search builds an LDB request, maps scope/attributes, applies GC or no-GC controls, handles extended-DN and notification controls, waits synchronously, queues entries/referrals, updates gMSA keys from controls, and emits `SearchResultDone`. Mutations convert LDAP structs into LDB messages, run transaction-wrapped requests, and queue result replies.

## State and Persistence Behavior

Connection state lives in `conn->ldb`, session info, LDB opaque values, pending notification calls, and reply queues. Add/modify/delete/rename persist through LDB transactions except on global catalog ports. Search can trigger persistent gMSA key updates after successful reads.

## Dependencies and Integration Points

It integrates LDAP protocol structures, GENSEC/SASL discovery, auth session info, SAMDB/LDB modules and controls, gMSA utilities, talloc, tsocket addresses, and authorization logging. It is called by the transport flow in `ldap_server.c`.

## Risks and Edge Cases

Search replies are capped at 256 MiB per call and written in chunks elsewhere, but memory can still grow until the cap. Notification searches persist in `pending_calls`. Mutations are synchronous and transaction-wrapped. `CompareRequest` relies on LDB filter formatting for value escaping. Expired sessions send an unsolicited notice and force session expiry handling.

## Test Signals

Tests should cover LDB error mapping, critical unknown controls, GC write rejection, search scope validation, extended DN, size-limit behavior, notifications, transaction rollback, compare true/false, abandon, authorization logging, encrypted connection opaque state, and expired session responses.
