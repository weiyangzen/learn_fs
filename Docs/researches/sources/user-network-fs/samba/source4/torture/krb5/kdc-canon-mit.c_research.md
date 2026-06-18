# sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-mit.c

## Purpose
This file is the MIT Kerberos variant of Samba's KDC canonicalization torture tests. It covers a narrower matrix than the Heimdal version, focusing on canonicalization, enterprise principals, uppercase usernames, UPNs, removed-dollar matching, and AS-REQ service principal behavior using MIT-compatible krb5 APIs.

## Important APIs, Types, and Functions
The test flags are `TEST_CANONICALIZE`, `TEST_ENTERPRISE`, `TEST_UPPER_USERNAME`, `TEST_UPN`, `TEST_REMOVEDOLLAR`, and `TEST_AS_REQ_SPN`. `struct test_data` mirrors the naming and flag state needed by each generated case. `struct torture_krb5_context` holds a Samba krb5 context and parsed target KDC address. `test_generate_session_info_pac()` and `test_accept_ticket()` match the Heimdal variant's purpose: decode PAC data without local database lookup and verify the accepted ticket's principal string through GENSEC.

MIT-specific API use includes `krb5_get_init_creds_opt_set_canonicalize(krb_options, ...)`, `smb_krb5_principal_set_type()`, `smb_krb5_principal_get_type()`, `smb_krb5_principal_get_comp_string()`, `smb_krb5_principal_get_realm()`, `krb5_get_credentials()`, and `krb5_mk_req_extended()`. `torture_krb5_init_context_canon()` initializes the Samba krb5 context and records the target KDC address, but unlike the Heimdal variant it does not install a packet-counting send override.

## Control Flow
Each generated case checks required torture settings, skips intentionally unsupported combinations, derives UPN or SPN principal strings, uppercases realm and optionally username, applies removed-dollar transformation when enabled, and computes canonical/expected principal strings. It parses principals with optional enterprise flags and sets principal types for SPN cases through Samba wrapper helpers.

The main test obtains initial credentials by password with the canonicalize option, verifies expected unknown-principal errors for non-UPN SPNs, removed-dollar restrictions, or required-canonicalization policy, then checks returned client principal type/name and krbtgt server principal structure. It stores the TGT in a memory ccache, obtains canonicalized credentials with `krb5_get_credentials()`, and then attempts to get a service ticket for the tested principal. For machine-account-capable cases it builds an AP-REQ using `krb5_mk_req_extended()` and verifies server-side PAC acceptance; otherwise it expects `KRB5KDC_ERR_S_PRINCIPAL_UNKNOWN`.

## State and Persistence Behavior
The test uses live KDC communication and memory credential caches. It does not persist database state or write files. It relies on the process credentials from Samba command-line parsing and on configured torture settings for optional UPN/SPN coverage.

## Dependencies and Integration Points
The file depends on MIT-compatible Kerberos behavior exposed through Samba wrappers, Samba's krb5 context, GENSEC krb5 server support, PAC decoding, command-line credentials, loadparm KDC policy options, and smbtorture suite generation. `torture_krb5_canon_mit()` registers the generated `canon` suite for MIT builds.

## Risks
MIT and Heimdal APIs differ, so this file intentionally avoids Heimdal-only send overrides, packet count assertions, Win2K option handling, S4U2Self matrix coverage, and some host referral checks. Environment provisioning remains a major source of skips/failures: UPN tests require `torture:krb5-upn`, SPN tests require hostname/service settings, removed-dollar tests require an explicit opt-in, and successful service-ticket/AP-REQ paths usually require a machine account with a servicePrincipalName. Loadparm canonicalization policy changes alter expected errors.

## Test Signals
Passing signals include expected initial-credential success or exact Kerberos errors, correct returned principal name/type, correct krbtgt component and realm handling, successful memory ccache storage, expected `krb5_get_credentials()` behavior, and successful GENSEC/PAC principal verification for machine-account service-ticket cases.
