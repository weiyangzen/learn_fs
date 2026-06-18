# sources/user-network-fs/samba/source4/torture/rpc/remote_pac.c

## Purpose
This file implements the `rpc.pac` torture sub-suite for remote Kerberos PAC validation through NETLOGON. It verifies that Samba can obtain a PAC through GENSEC/GSSAPI, parse the PAC into session information, validate PAC signatures through `netr_LogonSamLogon` generic information, reject tampered PAC payloads predictably, and preserve user/group details across normal Kerberos, S4U2Self, S4U2Proxy, and SamLogon flows. The tests cover both BDC and workstation secure-channel machine accounts and vary ARCFOUR, AES, and Kerberos-authenticated Netlogon setup paths.

## Important APIs, types, and functions
The local `struct pac_data` holds the raw `DATA_BLOB` PAC plus extracted server and KDC `PAC_SIGNATURE_DATA`. `test_generate_session_info_pac()` is a replacement `auth4_context.generate_session_info_pac` hook: it avoids local SAM token expansion, decodes `kerberos_pac_blob_to_user_info_dc()`, stores signatures in `auth_ctx->private_data`, and calls `auth_generate_session_info()`. `get_pac_buffer()` locates a PAC buffer by `PAC_TYPE`.

`test_PACVerify()` drives a GENSEC GSSAPI client/server exchange, extracts the PAC, checks mandatory PAC buffers such as logon info, logon name, UPN/DNS info, SRV/KDC/ticket/full checksums, and optional PKINIT credential info, then delegates to `netlogon_validate_pac()`. `netlogon_validate_pac()` builds `PAC_Validate`, sends it as `NetlogonGenericInformation`, and checks success plus negative cases for broken signature bytes, malformed length, wrong signature type, and wrong signature length.

Under `SAMBA4_USES_HEIMDAL`, `test_S4U2Self()` compares session info from kinit, S4U2Self, and SamLogon; `check_primary_group_in_validation()` validates the primary group RID is present in Netlogon validation groups. `test_S4U2Proxy()` checks constrained-delegation PAC buffers and `PAC_CONSTRAINED_DELEGATION` contents. `setup_constrained_delegation()` uses LDAP and SAMR to set `msDS-AllowedToDelegateTo` and `ACB_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`.

## Control flow
The suite factory `torture_rpc_remote_pac()` registers machine-join RPC test cases against `ndr_table_netlogon`. For each secure-channel variant it uses the RPC harness to create a temporary BDC or workstation account, connect to Netlogon, and pass the machine credentials into the PAC test function.

`test_PACVerify()` shallow-copies user and server credentials to isolate Kerberos memory ccaches, optionally loads `pkinit_ccache`, starts GENSEC client and server contexts with GSSAPI, and loops `gensec_update()` until authentication completes. It calls `gensec_session_info()` to trigger the custom PAC hook, parses the PAC with `ndr_pull_PAC_DATA`, validates expected buffer count and buffer presence, then calls `netlogon_validate_pac()`.

`netlogon_validate_pac()` either reconnects using `DCERPC_SCHANNEL | DCERPC_SCHANNEL_KRB5` when `NETLOGON_NEG_SUPPORTS_KERBEROS_AUTH` is requested or negotiates a normal Netlogon credential chain with `test_SetupCredentials2()` and `test_SetupCredentialsPipe()`. It NDR-encodes a `PAC_Validate` containing the server checksum and KDC signature, encrypts SamLogon payloads when appropriate, verifies `NT_STATUS_OK` for the intact PAC, then mutates the payload in controlled ways and asserts `NT_STATUS_LOGON_FAILURE` or `NT_STATUS_INVALID_PARAMETER` while checking credential chaining after each call.

The S4U2Self path performs three independent validations: a normal Kerberos GENSEC exchange, a GENSEC exchange using server credentials with `cli_credentials_set_impersonate_principal()`, and a Netlogon network SamLogon using NTLMv2 response material. It then compares account names, full names, domain SIDs, attributes, primary group presence, and asserted-identity/claims-valid SID behavior. S4U2Proxy prepares impersonation plus a distinct target service, performs a GENSEC exchange, validates a nine-buffer PAC including client claims and constrained delegation, then reuses Netlogon PAC validation.

## State and persistence
The file does not persist local state. Runtime state lives in talloc trees, temporary memory Kerberos ccaches, `auth_ctx->private_data`, Netlogon credential chains, and temporary domain machine accounts created by the harness. S4U2Proxy mutates directory state for the temporary machine account by writing `msDS-AllowedToDelegateTo` over LDAP and setting SAMR account flags; the test-join teardown owns cleanup. Settings that affect behavior include `pkinit_ccache` and `expect_pac_upn_dns_info`.

## Dependencies and integration points
This test depends on Samba auth, credentials, GENSEC, Kerberos/PAC parsing, Netlogon RPC, SAMR RPC, LDAP/SAMDB, and the torture RPC join helpers. It integrates with `rpc.c` through `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, `torture_rpc_tcase_add_test_creds()`, and `torture_rpc_tcase_add_test_join()`. It is registered into the global `rpc` suite by `torture_rpc_init()` in `rpc.c`.

## Risks
The tests are security-sensitive and compatibility-sensitive. Expected PAC buffer counts can change when KDC PAC contents evolve; the file partially gates this through `expect_pac_upn_dns_info` and PKINIT handling. Netlogon PAC validation still asserts ARCFOUR support for `PACValidate`, so negotiation changes can make AES/Kerberos cases fail before semantic validation. The S4U tests are compiled only with Heimdal support and assume constrained-delegation LDAP/SAMR mutations are permitted. Many assertions depend on exact SID ordering with special skips for asserted identity and claims-valid SIDs, so changes in PAC SID ordering may require corresponding test changes.

## Test signals
Strong pass signals are successful GENSEC handshakes, parsed PAC version `0`, expected PAC buffer counts, non-null checksum/signature buffers, `NetlogonGenericInformation` success for the intact PAC, and expected failure statuses for tampered payloads. S4U2Self additionally signals correctness through matching names, group SIDs, attributes, primary group inclusion, and expected authority/service asserted identity plus `SID_CLAIMS_VALID` counts. S4U2Proxy signals correctness by finding `PAC_TYPE_CONSTRAINED_DELEGATION`, expected proxy target, and one transited service before successful Netlogon PAC validation.
