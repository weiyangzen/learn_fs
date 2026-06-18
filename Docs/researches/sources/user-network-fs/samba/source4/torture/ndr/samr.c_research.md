# sources/user-network-fs/samba/source4/torture/ndr/samr.c

## Purpose

`samr.c` validates NDR parsing for selected SAMR RPC request and response payloads. It embeds captured wire blobs for connection, domain, user, password, and handle operations, with one detailed semantic check for a password-change rejection response.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_samr.h` and the generic torture NDR helpers.
- Static fixtures cover `samr_Connect5`, `samr_OpenDomain`, `samr_LookupNames`, `samr_OpenUser`, `samr_QueryUserInfo`, `samr_SetUserInfo`, `samr_SetUserInfo2`, `samr_GetUserPwInfo`, `samr_Close`, and `samr_ChangePasswordUser3`.
- `samr_changepassworduser3_w2k8r2_out_check()` validates `samr_DomInfo1`, `userPwdChangeFailureInformation`, and the final `NT_STATUS_PASSWORD_RESTRICTION`.
- `ndr_samr_suite()` registers input-only, output-only, and input/output pull tests using `torture_suite_add_ndr_pull_fn_test()` and `torture_suite_add_ndr_pull_io_test()`.

## Control Flow

The suite constructor registers each captured blob against its generated SAMR operation type and NDR direction. Most registered tests pass `NULL` as the semantic callback, so they check successful decoding only. `samr_QueryUserInfo` also has an input/output registration to validate combined call semantics. For `samr_ChangePasswordUser3`, the W2K request is decoded, a W2K response fixture is disabled, and the W2K8R2 rejection response is decoded with a callback that validates password policy fields and rejection reason.

## State and Persistence Behavior

The source is stateless apart from static fixtures. It does not contact SAMR, mutate account state, store handles, or persist results. Policy handles, SIDs, encrypted password buffers, and status codes are represented only as captured bytes decoded into generated structs.

## Dependencies and Integration Points

The file integrates generated SAMR NDR parsers with the NDR torture suite. It depends on SAMR constants such as `DOMAIN_PASSWORD_COMPLEX`, `SAM_PWD_CHANGE_NOT_COMPLEX`, and NTSTATUS comparison helpers. It exercises client/server marshalling contracts, not SAM database implementation logic.

## Risks and Edge Cases

- Most operations only verify that decoding succeeds; they do not assert handle UUIDs, access masks, RIDs, encrypted buffer sizes, or status values.
- The disabled W2K `ChangePasswordUser3` response notes a known parser failure or unsupported shape, leaving historical compatibility uncovered.
- Large encrypted payload fixtures are opaque; corruption inside fixed-size password buffers may not be detected unless parser length handling fails.
- Changes to SAMR IDL unions or password-info layouts can break these fixtures, but sparse assertions may not localize the changed field.

## Test Signals

The suite provides broad parser smoke coverage over common SAMR operations and one strong semantic check for password-policy rejection details. It is best interpreted as NDR compatibility coverage for captured traffic, with limited business-logic validation. Relevant signals are successful NDR pull of all registered blobs and exact assertions in `samr_changepassworduser3_w2k8r2_out_check()`.
