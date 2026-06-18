# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-lsa.h

## Purpose
`libsmb2-dcerpc-lsa.h` defines DCERPC Local Security Authority structures and coders used by libsmb2 for policy handles and SID lookup operations.

## Important APIs, Types, and Functions
It declares LSA opnums `LSA_CLOSE`, `LSA_OPENPOLICY2`, and `LSA_LOOKUPSIDS2`, policy access-mask flags, `RPC_SID`, translated-name/domain-list structures, `LSAPR_OBJECT_ATTRIBUTES`, request/reply structs for close/open-policy/lookup-SIDs, and coder functions such as `lsa_OpenPolicy2_req_coder()`, `lsa_LookupSids2_rep_coder()`, and `lsa_RPC_SID_coder()`.

## Control Flow
Runtime code builds request structs, encodes them with the declared coder for a DCERPC call, decodes reply structs, checks embedded NT status fields, and eventually closes context handles with `LSA_CLOSE`.

## State and Persistence Behavior
The header represents transient RPC data: policy context handles, SID arrays, translated names, referenced domains, and mapped counts. Memory ownership is managed by DCERPC/libsmb2 allocation and freeing routines.

## Dependencies and Integration Points
It depends on `libsmb2-dcerpc.h` types such as `ndr_context_handle`, `dcerpc_context`, `dcerpc_pdu`, and `smb2_iovec`. It integrates with LSA pipes over IPC$ and SID/name translation helpers.

## Risks and Edge Cases
NDR pointer and array counts must match server responses exactly. `MaxEntries` is documented as ignored. SID subauthority arrays and referenced-domain indexes are variable-length and require careful decode/free handling.

## Test Signals
Test opening policy with different desired access masks, resolving valid and unknown SIDs, multi-domain responses, zero-entry buffers, partial mapping status, and close-handle cleanup.
