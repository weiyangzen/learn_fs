# sources/user-network-fs/samba/source4/torture/ndr/nbt.c

## Purpose

`nbt.c` validates NDR decoding and selected round-trip encoding for NetBIOS-over-TCP Netlogon mailslot structures. It uses captured byte fixtures for legacy logon requests, logon responses, SAM logon responses, and primary domain controller queries, then asserts that generated `ndr_nbt` parsers interpret command discriminants, strings, SIDs, DNS-compressed names, site names, and LM token fields correctly.

## Important APIs, types, and functions

The file includes `torture/ndr/ndr.h` and generated `librpc/gen_ndr/ndr_nbt.h`. Important generated structures are `struct nbt_netlogon_packet`, `struct nbt_netlogon_response2`, and `struct netlogon_samlogon_response`. Local check callbacks include `netlogon_logon_request_req_check`, `netlogon_logon_request_resp_check`, `netlogon_samlogon_response_check`, `nbt_netlogon_packet_check`, `nbt_netlogon_packet_logon_primary_query_check`, and `netlogon_samlogon_response_check2`. `ndr_nbt_suite(TALLOC_CTX *ctx)` is the exported suite builder.

## Control flow

The suite builder registers simple pull tests for raw decode coverage and validate tests where the harness also pushes the decoded structure back to bytes and compares the result with the original fixture. The command field in `nbt_netlogon_packet` selects the active union member, so each check validates the correct branch: `LOGON_REQUEST`, `LOGON_SAM_LOGON_REQUEST`, and `LOGON_PRIMARY_QUERY`. SAM logon response fixtures validate `LOGON_SAM_LOGON_RESPONSE_EX` nested under the `nt5_ex` union arm.

## State and persistence

The file has no persistent state. Every test is deterministic and uses static fixture bytes plus stack-local expected GUID/SID values. SID creation uses `dom_sid_parse_talloc` with the torture context as allocator. GUID parsing uses `GUID_from_string` only to build expected values for comparison.

## Dependencies

Dependencies are the shared NDR torture harness, generated NBT NDR routines, Samba GUID and SID helpers, and NBT/Netlogon constants such as `LOGON_REQUEST`, `LOGON_RESPONSE2`, `NETLOGON_NT_VERSION_1`, and `LOGON_SAM_LOGON_RESPONSE_EX`.

## Integration points

`ndr_nbt_suite` is registered by `torture_local_ndr` in `ndr.c`. Its fixtures exercise the generated NBT parser used for Netlogon discovery traffic, especially mailslot discovery payloads and DNS-style encoded Netlogon response strings.

## Risks

Coverage is based on a small number of captured payloads. The suite does not test malformed compression pointers, malformed SIDs, unknown command discriminants, or short buffers. Some fields are documented in comments rather than directly asserted, for example the zero sockaddr details and next-closest-site nullability. Round-trip validation is present for several payloads, but not every fixture is registered as a validate test.

## Test signals

Important signals include exact command values, ASCII and Unicode workstation/domain names, mailslot names, domain GUIDs, domain SIDs, domain/PDC/site strings, LM token values, pad lengths, and full-consumption checks from the shared harness. Validate registrations add byte-for-byte push equivalence for selected SAM logon and packet fixtures.
