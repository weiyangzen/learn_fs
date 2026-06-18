# sources/user-network-fs/samba/source4/libnet/libnet_domain.c

## Purpose
`libnet_domain.c` provides composite libnet helpers for opening, closing, and listing domains over SAMR and LSA RPC pipes. It centralizes handle acquisition and caches active SAMR/LSA policy/domain handles in `struct libnet_context` for reuse by user/group/lookup operations.

## Important APIs, Types, And Functions
Public APIs are `libnet_DomainOpenSamr_send/recv()`, `libnet_DomainOpenLsa_send/recv()`, generic `libnet_DomainOpen_send/recv()` plus synchronous `libnet_DomainOpen()`, matching close APIs for SAMR/LSA/generic close, and `libnet_DomainList_send/recv()` plus synchronous `libnet_DomainList()`.

`domain_open_samr_state` carries RPC connect state, SAMR connect/lookup/open/close requests, domain SID, handles, access mask, and monitor callback. `domain_open_lsa_state` carries LSA open policy state. `domain_list_state` carries SAMR enumeration state, resume handle, collected domain list, and monitor callback.

## Control Flow
SAMR open first ensures a SAMR pipe exists, using `libnet_RpcConnect_send()` to a DC when needed. If an existing domain handle is cached in `ctx->samr`, it returns immediately when domain name and access mask match; otherwise it closes the old handle before reconnecting. The normal SAMR sequence is `samr_Connect`, `samr_LookupDomain`, then `samr_OpenDomain`.

LSA open similarly ensures an LSA pipe, then sends `lsa_OpenPolicy2` with a security QoS block. Generic open dispatches by `io->in.type`.

Close operations validate that the requested domain matches the cached `ctx->samr.name` or `ctx->lsa.name`, issue `samr_Close` or `lsa_Close`, and clear cached handle/name/SID state on success. Domain listing connects to SAMR on a target host if needed, calls `samr_Connect`, loops over `samr_EnumDomains` while `STATUS_MORE_ENTRIES` is returned, accumulates domain names, closes the SAMR connect handle, and returns the list.

## State And Persistence Behavior
This file maintains process-local RPC state in `libnet_context`: SAMR/LSA pipes, connect handles, domain handles, domain SID/name, and access masks. It does not write persistent storage. The cached handles affect later operations in the same libnet context and must be closed or replaced when a different domain/access mask is needed.

## Dependencies And Integration Points
The implementation depends on Samba composite contexts, generated SAMR and LSA RPC clients, `libnet_RpcConnect`, policy-handle helpers, talloc ownership, and monitor messages (`mon_SamrConnect`, `mon_SamrLookupDomain`, `mon_SamrOpenDomain`, `mon_LsaOpenPolicy`, close/enumeration events). Higher-level group/user/lookup functions depend on these helpers and on prerequisite wrappers such as `samr_domain_opened()` and `lsa_domain_opened()`.

## Risks
The handle cache makes behavior stateful: stale or mismatched cached handles can cause invalid-parameter returns or unintended close/reopen sequences. Some TODO comments note missing null-pipe checks in close paths. SAMR open requests `SEC_FLAG_MAXIMUM_ALLOWED` for `samr_OpenDomain` instead of the caller access mask after connect, which may matter against restrictive servers. `DomainList` accumulates names but does not resolve SIDs despite the output structure carrying a SID string field. Enumeration closes the connect handle after each page path, so resume behavior depends on server semantics and caller reentry.

## Test Signals
Tests should cover cached-handle reuse, changing access mask/domain forcing close and reopen, LSA and SAMR close mismatch errors, domain listing across `STATUS_MORE_ENTRIES`, monitor event ordering, and failure propagation when RPC call status differs from transport status. Existing user/group tests indirectly exercise this file through prerequisite domain-open helpers.
