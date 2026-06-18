# sources/user-network-fs/samba/source4/dsdb/common/rodc_helper.c

## Purpose
`rodc_helper.c` enforces whether a Read-Only Domain Controller is allowed to replicate secrets for a target account. It parses SID lists from RODC policy attributes and object token groups, applies deny/allow group policy, and protects krbtgt/trust accounts.

## Important APIs, Types, and Functions
- `sid_list_match()` checks for overlap between two SID arrays.
- `samdb_result_sid_array_ndr()` reads NDR-encoded SIDs from an LDB message attribute and prepends the object's primary SID.
- `samdb_result_sid_array_dn()` reads extended-DN SID components from attributes such as `msDS-NeverRevealGroup`.
- `samdb_confirm_rodc_allowed_to_repl_to_sid_list()` applies the core RODC reveal/never-reveal policy to a supplied token SID list.
- `samdb_confirm_rodc_allowed_to_repl_to()` builds the token SID list from `objectSid` and `tokenGroups`, then delegates.

## Control Flow
The core policy first denies attempts involving RODC krbtgt trust backlinks or inter-domain trust accounts. It verifies the alleged RODC account has `UF_PARTIAL_SECRETS_ACCOUNT`. It parses never-reveal and reveal-on-demand group SID lists from the RODC object. The RODC may replicate for itself. Any match with never-reveal denies. Any match with reveal-on-demand allows. Otherwise replication is denied.

The wrapper obtains the target object's primary SID, reads `tokenGroups` in NDR form while placing the primary SID at index zero, and invokes the core policy. Missing object SID or tokenGroups failures become DRA errors.

## State and Persistence
The module reads DSDB attributes but does not mutate them. Inputs are RODC account message attributes, target object account attributes, and token group SIDs. Results are WERROR policy decisions such as `WERR_OK`, `WERR_DS_DRA_SECRETS_DENIED`, `WERR_DOMAIN_CONTROLLER_NOT_FOUND`, and `WERR_DS_DRA_BAD_DN`.

## Dependencies and Integration Points
It depends on DCERPC server headers, generated security NDR, SAMDB helpers, Samba SID/security functions, `userAccountControl` flags, extended DN SID extraction, and replication/KDC callers that need RODC secret policy decisions.

## Risks and Edge Cases
- SID overlap is O(n^2), noted as acceptable for expected list sizes.
- Failure to parse reveal/never-reveal policy fails closed with secrets denied.
- The wrapper currently notes a TODO about whether `sIDHistory` should be considered.
- The core function indexes `token_sids[PRIMARY_USER_SID_INDEX]`; callers must supply a non-empty token SID array.

## Test Signals
Needed tests include RODC self-replication allow, never-reveal denial precedence, reveal-on-demand allow, default deny, non-RODC account rejection, krbtgt/trust-account denial, malformed SID attributes, missing tokenGroups/objectSid, and policy with overlapping groups.
