# sources/user-network-fs/samba/source3/rpc_client/util_netlogon.c

## Purpose
`util_netlogon.c` provides deep-copy and mapping helpers for Netlogon validation and domain-controller discovery structures. It is used to move authentication validation data between NETLOGON union levels and Samba server-info/auth layers without aliasing caller-owned memory.

## Important APIs, Types, And Functions
Exports are `copy_netr_SamBaseInfo()`, `copy_netr_SamInfo3()`, `copy_netr_SamInfo6()`, `map_validation_to_info3()`, `map_validation_to_info6()`, `map_info3_to_validation()`, `map_info6_to_validation()`, and `copy_netr_DsRGetDCNameInfo()`. The `COPY_LSA_STRING` macro duplicates optional LSA string fields.

## Control Flow
Base copy starts with a struct assignment, then deep-copies all pointer fields: account/full names, scripts, profile/home paths, group RID arrays, logon server/domain strings, and domain SID. Info3 and Info6 copy helpers allocate a fresh target, copy base info, then deep-copy extra SID arrays; Info6 also copies DNS domain and principal name. Validation mapping switches on validation level 3 or 6, either deep-copying the matching structure or constructing the other shape from the common base plus SID array. Info-to-validation helpers allocate a `union netr_Validation`, copy the info structure into the proper arm, and set validation level. DC name info copy duplicates all string fields, allowing optional forest/site names to remain NULL.

## State And Persistence
The file has no persistent state. All returned structures are talloc-owned under caller contexts. It intentionally avoids pointer aliasing from source validation data.

## Dependencies And Integration Points
Dependencies include generated Netlogon types, Samba security/SID helpers, talloc, and NTSTATUS memory macros. Callers include rpcclient Netlogon commands, winbind dual server handling, auth/server-info conversion paths, and code that copies DC locator results.

## Risks
The initial struct assignment in `copy_netr_SamBaseInfo()` copies pointer values before replacing known pointer fields; future generated struct changes could add pointer fields that require explicit deep-copy updates. The mapping helpers only accept validation levels 3 and 6 and return `NT_STATUS_BAD_VALIDATION_CLASS` otherwise. Output pointers are not cleared on failure, so callers should only consume them on OK status.

## Test Signals
Tests should verify deep-copy independence by freeing source structures after copy, level 3/6 validation mapping in both directions, SID and group array preservation, optional Info6 DNS/principal fields, unsupported validation-level errors, null validation errors, and DC locator copy behavior with optional NULL forest/site fields.
