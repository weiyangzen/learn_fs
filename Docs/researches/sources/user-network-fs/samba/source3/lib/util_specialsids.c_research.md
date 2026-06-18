# sources/user-network-fs/samba/source3/lib/util_specialsids.c

## Purpose
This file implements helpers for the Asserted Identity special SID namespace. It lets higher-level SID/name mapping code detect the asserted-identity domain SID itself or any SID whose domain portion is Asserted Identity.

## Important APIs and Functions
Exports are `sid_check_is_asserted_identity`, `sid_check_is_in_asserted_identity`, and `asserted_identity_domain_name`. The first compares directly with `global_sid_Asserted_Identity`; the second copies the input SID, strips the RID with `sid_split_rid`, and compares the remaining domain SID; the third returns the display domain string `"Asserted Identity"`.

## Control Flow and State
The implementation is stateless and deterministic. It performs no allocation except stack storage for the copied domain SID, and it does not persist data.

## Dependencies and Integration Points
It depends on `dom_sid_equal`, `sid_copy`, `sid_split_rid`, and the global SID constants from `../libcli/security/security.h`. It integrates with source3 SID mapping and name lookup paths that need to recognize Windows special identities.

## Risks and Test Signals
The main edge case is malformed or RID-less SIDs: `sid_split_rid` return value is ignored, so tests should cover exact domain SID, domain plus RID, unrelated SIDs, and empty or minimal SID shapes. A null `sid` is not guarded locally and must be prevented by callers.
