# sources/user-network-fs/samba/source4/torture/rpc/samlogon.c

## Purpose

`samlogon.c` is a Samba RPC torture test for Netlogon `SamLogon` behavior. It validates how a domain controller handles network and interactive logon requests over the Netlogon RPC interface, with particular focus on NTLM-family challenge/response combinations, returned session keys, credential chaining, workstation and logon-time restrictions, machine-account logons, different username syntaxes, and schannel credential negotiation modes.

The test creates temporary directory state, joins a workstation account named `samlogontest`, creates several test users, adjusts account policy to allow immediate password changes, and then drives `netr_LogonSamLogon`, `netr_LogonSamLogonEx`, and `netr_LogonSamLogonWithFlags` calls through many combinations of validation level, logon level, authentication response shape, and secure-channel credential flags.

## Important APIs, Types, and Data

- `enum ntlm_break` models intentional response corruption or omission: `BREAK_BOTH`, `BREAK_NONE`, `BREAK_LM`, `BREAK_NT`, `NO_LM`, and `NO_NT`.
- `struct samlogon_state` is the per-test carrier for talloc context, torture context, account identity, password, workgroup and NetBIOS names, Netlogon pipe, selected function level, parameter-control flags, prebuilt request structures for all three SamLogon RPC variants, Netlogon authenticators, credential state, expected status, old-password tolerance, and the server challenge.
- `check_samlogon()` is the core dispatcher. It populates `netr_NetworkInfo`, optionally corrupts or removes LM/NT responses, calls the selected Netlogon RPC, verifies returned authenticators where the RPC variant uses credential chaining, decrypts the returned SamLogon validation blob, extracts the `netr_SamBaseInfo`, and returns both NT status and session-key material to the caller.
- `test_table[]` lists the network-logon subtests. Entries cover LM, NTLM, LM+NTLM, NTLM-in-LM, NTLM-in-both, NTLMv2, LMv2, mixed NTLM/LMv2 cases, intentionally broken responses, NTLM2 session-security material, and plaintext-password-in-response-field cases.
- `test_SamLogon()` builds common request state and runs every enabled `test_table` case across validation levels `2`, `3`, and `6`, logon levels `NetlogonNetworkInformation` and `NetlogonNetworkTransitiveInformation`, and function levels `NDR_NETR_LOGONSAMLOGON`, `NDR_NETR_LOGONSAMLOGONEX`, and `NDR_NETR_LOGONSAMLOGONWITHFLAGS`.
- `test_InteractiveLogon()` exercises `netr_LogonSamLogonWithFlags` with `NetlogonInteractiveTransitiveInformation`, encrypted `netr_PasswordInfo`, validation level `6`, and explicit authenticator verification.
- `handle_minPwdAge()` uses SAMR RPC to read and change `DomainPasswordInformation.min_password_age`, storing the old value in a static local so the main test can restore it.
- `torture_rpc_samlogon()` is the exported torture entry point. It provisions test accounts, opens the Netlogon pipe, runs the interactive and network logon matrix, reruns selected cases under different Netlogon credential flags, and cleans up joins and policy changes.

The file depends on generated NDR client stubs from `ndr_netlogon_c.h` and `ndr_samr_c.h`, torture RPC helpers from `torture/rpc/torture_rpc.h`, secure-channel credential helpers from `auth/gensec/gensec.h` and `libcli/auth/libcli_auth.h`, command-line credentials, Samba loadparm accessors, and GnuTLS MD5/HMAC primitives used by the NTLM2-session-security test.

## Control Flow

The main path starts in `torture_rpc_samlogon()`. It first calls `handle_minPwdAge(..., true)` so the generated test user password can be changed immediately. It joins a workstation trust account, creates the primary test user, changes that user's password to a long password, creates a user restricted to a different workstation, and creates a user with all logon-hour bits cleared. The wrong-workstation and wrong-time accounts are configured through SAMR `SetUserInfo` level `21`.

The Netlogon binding is then forced to schannel with signing, sealing, and 128-bit mode before connecting as the joined machine account. The machine credentials provide `netlogon_creds_CredentialState`, which is reused by both interactive and network logon tests.

For each user-credential scenario in the local `usercreds[]` table, the test first performs an interactive logon via `test_InteractiveLogon()`. If the scenario is marked `network_login`, it then invokes `test_SamLogon()` for the full network-logon matrix. The scenario table intentionally covers normal command-line user forms, realm forms, UPN forms, machine-account forms with and without `MSV1_0_ALLOW_WORKSTATION_TRUST_ACCOUNT`, long-password test-user forms, an old-password oddball case, and workstation restriction failure.

After the broad matrix, `torture_rpc_samlogon()` repeats a narrower sample using different credential negotiation flags: default auth2 flags, ARCFOUR, ARCFOUR plus 128-bit, ADS auth2 flags, and zero flags for DES-style behavior. It then clears cached Netlogon credentials, reconnects using Kerberos schannel, and runs the same selected interactive and network checks.

`test_SamLogon()` performs nested loops over function level, subtest, validation level, and logon level. It creates a fresh talloc context for each inner iteration, updates the shared `samlogon_state`, calls the selected subtest function, logs detailed identifying context on failure, and treats `test_table[].expect_fail` as a way to report incomplete expected failures without failing the whole suite.

All network subtest helpers eventually call `check_samlogon()`. That helper wires the response blobs into `netr_NetworkInfo`, applies the requested break/omit behavior, dispatches to the chosen RPC, handles transport status separately from the RPC result, validates returned authenticators for credential-chained variants, decrypts the returned validation data using the negotiated DCERPC auth type and level, and exposes the `base.key` and `base.LMSessKey` fields for session-key assertions.

## Authentication Cases and Expected Signals

NTLMv1-style helpers construct LM and NT responses with `SMBencrypt()`, `SMBNTencrypt()`, `E_deshash()`, `E_md4hash()`, and `SMBsesskeygen_ntv1()`. They verify whether broken or omitted responses produce `NT_STATUS_WRONG_PASSWORD`, expected scenario-specific statuses, or successful validation with the correct user session key and LM session key behavior. Long passwords, old passwords, and modern servers that reject LM-only behavior have explicit compatibility branches.

NTLMv2 and LMv2 helpers use `NTLMv2_generate_names_blob()` and `SMBNTLMv2encrypt()` with either the account domain or an empty domain. They validate that a successful SamLogon returns the NTLMv2 session key for normal cases, the LMv2 key for LMv2-only cases, and all-zero or failed key behavior where intentionally broken response fields should be ignored or rejected.

`test_lmv2_ntlm_broken()` covers mixed LMv2 and NTLMv1 responses and asserts which key source wins under normal, broken-LM, broken-NT, and omitted-NT cases. `test_ntlm2()` crafts NTLM2 session-security style input by placing an MD5-derived nonce in the LM response and computing an HMAC-MD5 expected value, but the asserted behavior is that Netlogon should return the plain NT key rather than applying NTLM2 session security inside SamLogon.

`test_plaintext()` sends plaintext password material in the LM and NT response fields when `MSV1_0_CLEARTEXT_PASSWORD_ALLOWED` is added to `parameter_control`. It converts the password into UTF-16LE-like UCS-2 for the NT field and uppercase DOS encoding for the LM field, then checks success or expected failure under the same broken/omitted response modes.

`test_InteractiveLogon()` encrypts password hashes with `netlogon_creds_encrypt_samlogon_logon()`, calls `netr_LogonSamLogonWithFlags`, verifies the returned authenticator, and compares the RPC result with the caller's expected interactive status. It does not inspect session keys in the same detailed way as the network-logon matrix.

## State and Persistence Behavior

This file intentionally mutates directory and domain state during the test:

- It joins a temporary workstation trust account named `samlogontest`.
- It creates normal test users `samlogontestuser`, `samlogontest2`, and `samlogontest3`.
- It changes the primary test user's password to a generated long password and keeps the previous password for old-password acceptance/rejection checks.
- It sets `samlogontest2` to allow logon only from a workstation name that does not match the test machine.
- It sets `samlogontest3` with workstation and logon-hour restrictions, although the visible `usercreds[]` matrix in this file does not include a later explicit credential scenario for that account.
- It temporarily sets domain `minPwdAge` to zero and restores the previously observed value on exit.

Runtime memory is managed through nested talloc contexts. `test_SamLogon()` creates a function-level context and an inner-loop context per subcase so response blobs and temporary strings do not persist across cases. `handle_minPwdAge()` uses a static `old_minPwdAge`, so a restore call assumes the same process previously made a successful set call.

Cleanup is performed after the `failed:` label in `torture_rpc_samlogon()`: the domain password age is restored, `mem_ctx` is freed, and all join/user contexts are passed to `torture_leave_domain()`. Because the function uses `torture_assert()` for the final min-password-age restore, a restore failure is itself a hard test failure.

## Dependencies and Integration Points

This test integrates with Samba's torture framework and expects a writable test domain controller environment. It relies on:

- Netlogon RPC generated client calls: `dcerpc_netr_LogonSamLogon_r()`, `dcerpc_netr_LogonSamLogonEx_r()`, and `dcerpc_netr_LogonSamLogonWithFlags_r()`.
- SAMR RPC calls for policy and user setup: `Connect`, `LookupDomain`, `OpenDomain`, `QueryDomainInfo`, `SetDomainInfo`, `SetUserInfo`, and `Close`.
- Torture provisioning helpers such as `torture_join_domain()`, `torture_create_testuser()`, `torture_join_samr_pipe()`, `torture_join_samr_user_policy()`, `test_ChangePasswordUser3()`, and `test_SetupCredentials2()`.
- Credential and secure-channel helpers: `cli_credentials_get_netlogon_creds()`, `netlogon_creds_client_authenticator()`, `netlogon_creds_client_verify()`, `netlogon_creds_encrypt_samlogon_logon()`, `netlogon_creds_decrypt_samlogon_validation()`, and DCERPC binding auth metadata.
- Command-line user credentials from `samba_cmdline_get_creds()` and loadparm values such as workgroup, realm, and NetBIOS name.
- Cryptographic helpers from Samba's NTLM implementation plus GnuTLS hash/HMAC calls.

The file is not a general-purpose library; it is consumed by the RPC torture suite as a test entry point. Its successful execution depends on appropriate privilege to create accounts, join a workstation, alter domain password policy, set SAMR user fields, and establish schannel-protected Netlogon RPC connections.

## Risks and Edge Cases

- Domain mutation is broad for a test: failure before cleanup can leave altered password policy or temporary accounts if lower-level cleanup helpers do not run or fail.
- `handle_minPwdAge()` stores the old value in a process-static variable and returns `false` on initial connection failure, so restoration depends on the earlier successful set path and the same process lifetime.
- The wrong-logon-hours user is configured but not included in the visible `usercreds[]` scenarios, which suggests either dead setup, an incomplete test case, or a scenario handled elsewhere in historical versions.
- Many branches tolerate different server behavior for old passwords, long passwords, LM-only cases, Samba3 versus modern Samba behavior, and UPN forms. These compatibility allowances reduce false positives but can also mask regressions if expectations become too broad.
- `check_samlogon()` mutates response blobs in place when breaking LM or NT responses. Callers generally allocate fresh blobs per invocation, which makes this safe, but reuse would be hazardous.
- The test matrix is large: function levels multiplied by subtests, validation levels, logon levels, credential scenarios, and credential flags. Runtime and diagnosability depend on the torture harness output being preserved.
- The test assumes returned validation levels `2`, `3`, or `6` map to populated `sam2`, `sam3`, or `sam6` arms. Unexpected validation-level behavior becomes an invalid-parameter style failure.
- Cryptographic expectations are byte-exact and sensitive to negotiated auth type, auth level, and server policy around LM responses.

## Test Signals

Primary pass/fail signals are torture assertions, `NTSTATUS` comparisons, and byte comparisons of returned session keys:

- Transport-level RPC status must be OK before RPC result status is interpreted.
- Credential-chained calls must return a non-null authenticator and pass `netlogon_creds_client_verify()`.
- Successful SamLogon responses must decrypt through `netlogon_creds_decrypt_samlogon_validation()`.
- Expected failures must match scenario-specific statuses such as `NT_STATUS_WRONG_PASSWORD`, `NT_STATUS_INVALID_WORKSTATION`, `NT_STATUS_NO_SUCH_USER`, or `NT_STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT`.
- Session keys must match the expected NTLMv1, NTLMv2, LMv2, LM-hash-derived, zero, or NT-key behavior for each response arrangement.
- The credential-flag pass confirms that session-key encryption works under multiple Netlogon negotiation modes.
- The final Kerberos schannel pass confirms the same selected behavior when the secure channel is established with `DCERPC_SCHANNEL_KRB5`.
