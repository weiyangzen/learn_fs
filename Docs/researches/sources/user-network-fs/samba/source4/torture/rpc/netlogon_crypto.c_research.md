# sources/user-network-fs/samba/source4/torture/rpc/netlogon_crypto.c

## Purpose

`netlogon_crypto.c` defines a focused FIPS/weak-crypto torture suite for Netlogon secure-channel authentication. It verifies that AES negotiation succeeds and that RC4/ARCFOUR negotiation is rejected or unavailable when weak crypto is not allowed.

## Important APIs, Types, and Functions

The central helper is `test_ServerAuth3Crypto()`. It performs a complete `ServerReqChallenge` and `ServerAuthenticate3` flow, but parameterizes the negotiate flags and whether client-side RC4 should be forced. It uses `netlogon_creds_client_init()` for credential derivation, `GNUTLS_FIPS140_SET_LAX_MODE()`/`GNUTLS_FIPS140_SET_STRICT_MODE()` around forced RC4, and `lpcfg_weak_crypto()` to adapt assertions to the configured weak-crypto policy.

The public suite factory is `torture_rpc_netlogon_crypto_fips()`. It registers:

- `test_AES_Crytpo`: requests ADS flags plus `NETLOGON_NEG_SUPPORTS_AES` and expects success.
- `test_RC4_Crytpo_Fail`: requests ADS flags plus `NETLOGON_NEG_ARCFOUR` and expects client credential initialization to fail when weak crypto is disabled.
- `test_RC4_Crytpo_Force`: forces lax FIPS mode client-side so the server response can be tested; when weak crypto is disabled, the expected server result is `NT_STATUS_DOWNGRADE_DETECTED` with negotiated flags cleared.

## Control Flow

Each test receives a machine-backed Netlogon pipe from `torture_suite_add_machine_bdc_rpc_iface_tcase()`. The helper generates a client challenge, calls `ServerReqChallenge`, hashes the machine password with `E_md4hash()`, prepares `ServerAuthenticate3`, derives client credential state, and calls the RPC. It then validates server credential chaining and negotiated flags.

The RC4 paths invert the normal success condition: if RC4 setup or authentication fails for the expected policy reason, the test wrapper returns success. If RC4 unexpectedly succeeds while weak crypto is disabled, the wrapper fails.

## State and Persistence Behavior

The file does not persist server state or change account passwords. It temporarily changes the process crypto mode with GnuTLS FIPS helpers during forced RC4 client credential creation, then restores strict mode. The main mutable state is the local Netlogon credential state and negotiated flags.

## Dependencies and Integration Points

The file depends on Samba generated Netlogon RPC clients, libcli auth helpers, loadparm weak-crypto policy, GnuTLS FIPS-mode macros exposed through Samba headers, and the torture machine-account RPC testcase helper.

It complements the larger `netlogon.c` suite by isolating crypto-policy behavior under a separate `fips.netlogon.crypto` suite name.

## Risks and Edge Cases

The expected result depends on `lpcfg_weak_crypto(tctx->lp_ctx)`. In environments where weak crypto is explicitly allowed, RC4 behavior will differ from hardened/FIPS expectations.

The helper intentionally relaxes FIPS mode to manufacture a forced-RC4 client request. A failure to restore strict mode would leak process crypto policy into later tests, but the code unconditionally calls `GNUTLS_FIPS140_SET_STRICT_MODE()` after credential initialization.

The registered test names contain `Crytpo` rather than `Crypto`; this affects test naming/discovery but not behavior.

## Test Signals

Success is signaled by AES negotiation including `NETLOGON_NEG_SUPPORTS_AES`, by client-side RC4 credential initialization failing when weak crypto is prohibited, or by server-side forced RC4 returning `NT_STATUS_DOWNGRADE_DETECTED`. Credential-chain validation is the main integrity signal for successful authentication.
