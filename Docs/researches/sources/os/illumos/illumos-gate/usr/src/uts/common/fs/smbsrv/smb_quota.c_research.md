# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_quota.c

## Purpose

`smb_quota.c` implements SMB quota query/set support helpers. It decodes SID lists and quota entries from SMB wire buffers, encodes quota responses, maintains per-ofile quota resume state, maps local UIDs to SIDs for user quota queries, and calls userland quota services via SMB kernel door upcalls.

## Main Interfaces

- `smb_quota_init_sids()` initializes a query SID list based on query operation.
- `smb_quota_free_sids()` releases decoded SID lists.
- `smb_quota_decode_sids()` decodes client-provided SID entries.
- `smb_quota_max_quota()` derives maximum requested quota entries from response buffer size and query flags.
- `smb_quota_decode_quotas()` decodes quota entries for set operations.
- `smb_quota_free_quotas()` releases quota lists.
- `smb_quota_encode_quotas()` encodes quota query responses and updates resume SID.
- `smb_quota_query_user_quota()` queries quota for a single local UID.
- `smb_quota_query()` and `smb_quota_set()` perform door upcalls.

## Behavior And Data Flow

SID-list and quota-list decoders walk variable-length entries using `next_offset`, shadow the mbuf chain at each entry, decode fixed fields, decode SIDs from calculated offsets, convert them to SID strings, and append typed objects to illumos lists. Query initialization either decodes explicit SID lists, decodes a start SID, or resumes from the ofile's stored quota resume SID for query-all.

Quota encoding converts SID strings back to `smb_sid_t`, calculates fixed size plus SID length plus 8-byte padding, checks output room, encodes fixed fields and SIDs, pads entries, sets the last entry's `next_offset` to zero, and stores the last emitted SID as resume state for start/all queries.

Single-user quota lookup maps a local UID to a SID, constructs a SID-list query rooted at the tree mount path, calls the userland quota door service, validates that the returned quota matches the requested SID, copies it out, and frees XDR-owned reply structures.

## Dependencies

This file depends on SMB mbuf-chain shadowing and encoding, SID encode/decode/string conversion, idmap UID-to-SID mapping, SMB tree mount path helpers, `smb_kdoor_upcall`, XDR routines for quota requests/responses, and ofile quota resume accessors.

## Notable Invariants And Risks

- Quota wire entries use fixed fields plus variable SID data and 8-byte alignment.
- Decode loops trust `next_offset` progression and `bytes_left`; malformed offsets must be rejected by mbuf shadow/decode failures.
- Query-all without restart requires a valid stored resume SID or returns `NT_STATUS_INVALID_PARAMETER`.
- `SMB_QUOTA_QUERY_SIDLIST` ignores `qq_max_quota`; start/all derive it from response buffer capacity unless single-entry is requested.
- Door call return `0` means transport/XDR success; operation status is carried separately in the reply.
