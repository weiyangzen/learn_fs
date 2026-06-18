<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid.c -->
# sources/user-network-fs/samba/source3/lib/util_sid.c

## Purpose
`util_sid.c` provides SID serialization, filtering, token SID-array construction from Netlogon info3 data, and Samba NPA flag helpers.

## Important APIs, types, and functions
Public functions include `sid_to_fstring`, `sid_linearize`, `non_mappable_sid`, `sid_binstring_hex_talloc`, `sid_array_from_info3`, `security_token_find_npa_flags`, and `security_token_del_npa_flags`.

## Control flow
SID string and binary helpers use Samba NDR and SID formatting routines. `non_mappable_sid` checks whether a SID belongs to BUILTIN or NT Authority domains. `sid_array_from_info3` optionally adds the user SID, always adds primary group SID, adds supplemental group RIDs, then copies extra SIDs while skipping asserted identity SIDs to avoid privilege elevation. NPA helpers count flag SIDs under `global_sid_Samba_NPA_Flags`, extract the RID as flags, or remove the flag SID from a token.

## State and persistence behavior
Functions allocate caller-owned talloc arrays/strings or mutate the supplied security token when deleting NPA flags. No persistent state is written.

## Dependencies and integration points
It depends on generated NDR security/netlogon types, SID helpers, special SID predicates, token SID-array utilities, and string wrappers. Authentication and idmap code use it when building tokens from domain logon responses.

## Risks and edge cases
SID composition failures return invalid parameter. Extra SID filtering is important for security. `security_token_del_npa_flags` asserts exactly one NPA flag SID, so callers must check or guarantee presence first.

## Test signals
Tests should cover NDR linearization buffer sizing, non-mappable domain checks, info3 SID array construction with and without user SID, duplicate primary/additional groups, asserted identity filtering, and NPA flag find/delete behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid.c -->
