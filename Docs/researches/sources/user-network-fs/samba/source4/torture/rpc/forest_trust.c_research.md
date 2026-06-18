# sources/user-network-fs/samba/source4/torture/rpc/forest_trust.c

## Purpose
This file defines the `rpc.lsa.forest.trust` suite. It creates LSA trusted-domain objects, sets and queries forest-trust information, validates trust secrets over Netlogon, and optionally creates reciprocal trusts between two domains when secondary binding and credential options are supplied.

## Important APIs, Types, And Functions
`torture_rpc_lsa_forest_trust()` registers `ForestTrust` on `ndr_table_lsarpc`. `test_get_policy_handle()` uses `lsa_OpenPolicy3` with revision information and checks AES trust-auth support. `test_create_trust_and_set_info()` drives `lsa_CreateTrustedDomainEx2`, `lsa_QueryTrustedDomainInfo`, `test_set_forest_trust_info()`, and `test_query_forest_trust_info()`. `get_trust_domain_passwords_auth_blob()` builds a `trustDomainPasswords` NDR blob. `test_setup_trust()` RC4-encrypts that blob with the RPC session key before creating the trust. `test_validate_trust()` uses Netlogon secure-channel setup, `netr_ServerGetTrustInfo`, and `netr_GetForestTrustInformation`.

## Control Flow
`testcase_ForestTrusts()` generates a random trust password, creates an auth blob, parses a fixed test SID, and creates a dummy forest trust on the primary target. It then queries local DNS policy info, exercises query/set info levels, validates the trust over Netlogon using the generated password, and deletes the dummy trust. If `torture:Forest_Trust_Dom2_Binding` and `torture:Forest_Trust_Dom2_Creds` are present, it connects to the second domain, verifies the domains differ, creates reciprocal trusts, validates both directions, and deletes both trusts.

## State And Persistence Behavior
The test intentionally creates and deletes trusted-domain objects. It sets forest-trust top-level-name and domain-info records, writes trust authentication information, and can install reciprocal forest trusts across two real domains. Cleanup is explicit through `delete_trusted_domain_by_sid()`, but early assertion failures can leave trust objects behind. The password blob contains incoming and outgoing current trust secrets; no previous secret is set.

## Dependencies And Integration Points
Dependencies include LSA, DRS blob definitions for trust-password structures, Netlogon RPC, credential and secure-channel helpers, Samba LSA initializer helpers, GnuTLS ARCFOUR, generated random passwords, SID parsing, and torture settings for primary/secondary bindings. It integrates tightly with Active Directory domain policy and Netlogon credential validation.

## Risks And Edge Cases
This is an invasive administrative test. It requires privileges to create and delete trusts and can change real trust topology. `LSA_TRUST_ATTRIBUTE_FOREST_TRANSITIVE` behavior differs by server functional level, and unsupported encryption-type info can cause early success return in `get_and_set_info()`. The file uses a fixed dummy SID and names, so stale objects from previous failures can affect `check_name()` or creation.

## Test Signals
Signals include `OpenPolicy3` revision and feature checks, exact trusted-domain info fields, absence of forest-trust collision info, expected query/set results for supported info levels, successful decryption and comparison of new/old OWF trust passwords, expected forest trust records from Netlogon, and successful deletion by SID.
