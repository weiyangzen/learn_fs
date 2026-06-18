# sources/user-network-fs/samba/source3/include/lsa.h

## Purpose
`lsa.h` provides a small helper surface for the Local Security Authority RPC server code. It focuses on building LSA reference-domain lists and normalizing lookup error handling.

## Important APIs, Types, And Control Flow
The single function declaration, `init_lsa_ref_domain_list()`, initializes a generated `lsa_RefDomainList` from a domain name and domain SID under a caller-provided talloc context. The `NT_STATUS_LOOKUP_ERR(status)` macro treats any status other than success, `STATUS_SOME_UNMAPPED`, and `NT_STATUS_NONE_MAPPED` as a hard lookup error, matching LSA lookup APIs where partial or complete unmapped results can still be valid protocol outcomes.

## State And Persistence
The header itself stores no state. Runtime allocation is caller-owned through `TALLOC_CTX`; resulting LSA structures are transient RPC response data rather than persistent database state.

## Dependencies And Integration Points
It depends on Samba NTSTATUS macros, generated LSA NDR structures, domain SID types, and talloc conventions. It integrates with LSA name/SID lookup RPC handlers and passdb/idmap lookup flows that must return Windows-compatible partial mapping statuses.

## Risks And Test Signals
Risks are concentrated in status classification: treating partial mapping as fatal would break Windows-compatible lookup responses, while missing real errors would hide backend failures. Test signals include lookup calls returning all mapped, some unmapped, none mapped, and backend error cases; memory ownership checks for the allocated reference-domain list; and RPC response validation against generated LSA marshalling.
