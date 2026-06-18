<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c

## Purpose

`ntlm_auth_diagnostics.c` is a diagnostic harness for the `ntlm_auth` utility. It synthesizes LM, NTLM, LMv2, NTLMv2, and plaintext-in-response-field authentication attempts, sends them through `contact_winbind_auth_crap()`, and verifies whether authentication and returned session keys match expectations.

## Important APIs, Types, and Functions

`enum ntlm_break` describes deliberate test mutations: no mutation, broken LM, broken NT, no LM, or no NT. `diagnose_ntlm_auth()` is the exported entry point. `test_lm_ntlm_broken()`, `test_ntlm_in_lm()`, `test_ntlm_in_both()`, `test_lmv2_ntlmv2_broken()`, and `test_plaintext()` perform the main protocol variants. `test_table[]` orders all diagnostic cases and marks tests that should only pass when LM support is expected.

## Control Flow

`diagnose_ntlm_auth()` iterates `test_table[]`, passes the caller's LANMAN expectation into each test, and fails the overall result if a required test fails or an LM-only test unexpectedly passes when LM support should be disabled. Each test builds a challenge with `get_challenge()`, derives responses and expected keys from the process-global username/domain/password, optionally corrupts or removes one response, calls winbind through `contact_winbind_auth_crap()`, and compares returned LM/user session keys to expected hashes or NTLMv2 session keys.

## State and Persistence Behavior

The diagnostics code does not persist account state. It consumes the process-global option values declared in `ntlm_auth.h` and uses talloc stack allocations for blobs. Authentication attempts may update winbind-side bad password counters or logs because deliberately corrupted responses are sent to the real authentication backend.

## Dependencies and Integration Points

It depends on Samba NTLM crypto helpers (`SMBencrypt`, `SMBNTencrypt`, `SMBNTLMv2encrypt`, `E_deshash`, `E_md4hash`, `SMBsesskeygen_ntv1`), `contact_winbind_auth_crap()` from `ntlm_auth.c`, winbind status flags, and debug/dump utilities. It also uses `get_winbind_netbios_name()` and `get_winbind_domain()` to build NTLMv2 target names.

## Risks and Edge Cases

Diagnostics are live authentication attempts, not offline unit tests. Broken-response cases can trigger account lockout policy or misleading audit noise. Expected LM-key behavior differs by server capability, so the `lanman_support_expected` input must match the environment. The plaintext diagnostic uses a zero challenge and `MSV1_0_CLEARTEXT_PASSWORD_ALLOWED`, so policy changes around cleartext auth will affect results.

## Test Signals

The file is itself a test signal for the wider authentication chain. Useful coverage includes running diagnostics with `--request-lm-key` against an LM-capable server, without it against Samba AD-style behavior, and under bad-password lockout policy in a controlled account to confirm broken cases do not accidentally pass.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c -->
