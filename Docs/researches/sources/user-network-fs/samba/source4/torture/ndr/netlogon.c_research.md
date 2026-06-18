# sources/user-network-fs/samba/source4/torture/ndr/netlogon.c

## Purpose

`netlogon.c` is a fixture-driven local NDR torture suite for generated Netlogon RPC structures. It validates request and response decoding for secure-channel challenge/authentication, interactive logon, and domain information exchange. It also exercises NDR64 layout for `netr_LogonGetDomainInfo` and preserves known failure cases in disabled blocks.

## Important APIs, types, and functions

The suite includes `librpc/gen_ndr/ndr_netlogon.h` and uses registration macros from `ndr.h`. Important callbacks include `netrserverauthenticate3_in_check`, `netrserverauthenticate3_out_check`, `netrserverreqchallenge_in_check`, `netrserverreqchallenge_out_check`, `netrlogonsamlogon_w2k_in_check`, `netrlogongetdomaininfo_in_check`, `netrlogongetdomaininfo_out_check_common`, `netrlogongetdomaininfo_out_check`, `netrlogongetdomaininfo_out_check64`, and `netrlogongetdomaininfo_in_check_osversion`. The suite builder is `ndr_netlogon_suite(TALLOC_CTX *ctx)`.

## Control flow

`ndr_netlogon_suite` registers direction-specific pull tests for `netr_ServerReqChallenge`, `netr_ServerAuthenticate3`, `netr_LogonSamLogon`, and `netr_LogonGetDomainInfo`. For domain info it also registers in/out tests so the request fixture is decoded first and the response fixture is decoded with request context. The NDR64 variants pass `LIBNDR_FLAG_NDR64` through the shared harness. Some known problematic round-trip or response cases remain inside `#if 0` blocks and do not execute.

## State and persistence

All test data is static. Credential, challenge, password hash, authenticator, GUID, and SID expected values are stack-local. The file does not establish a Netlogon secure channel or persist machine account state; it only decodes captured RPC payloads. In/out tests reuse one decoded structure across request and response parsing to model RPC context.

## Dependencies

Dependencies include generated Netlogon NDR routines and constants, Samba torture assertions, SID/GUID helpers such as `string_to_sid` and `GUID_from_string`, LSA trust constants referenced by trust-extension assertions, and shared NDR harness support for NDR64 and in/out decoding.

## Integration points

`ndr_netlogon_suite` is registered by the top-level local NDR suite in `ndr.c`. The fixtures guard generated IDL behavior for Netlogon RPC calls used in domain controller discovery, secure channel establishment, and domain trust information transfer.

## Risks

Some input callbacks intentionally return true without asserting fields, notably base `netr_LogonGetDomainInfo` input and the OS-version NDR64 input. The W2K validation-level-6 SAM logon response is disabled with a comment that Samba currently fails to parse it. A NDR64 pull/push test for OS-version data is also disabled because pointer value calculations likely fail. These disabled paths are valuable risk markers around pointer layout, response validation, and NDR64 round-trip behavior.

## Test signals

Strong signals include exact server/computer/account names, credentials and return credentials, negotiate flags, RID and NTSTATUS checks, interactive logon identity strings, LM/NT password hashes, validation level, return authenticators, primary and trusted domain names, DNS forest/domain names, GUIDs, SIDs, trust extension flags/type/attributes, supported encryption type differences between NDR32 and NDR64 fixtures, full-consumption checks, and in/out response-context parsing.
