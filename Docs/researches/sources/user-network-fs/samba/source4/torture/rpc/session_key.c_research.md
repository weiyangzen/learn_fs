# sources/user-network-fs/samba/source4/torture/rpc/session_key.c

## Purpose

This file defines the `lsa.secrets` torture suite. It verifies that LSA secret encryption and decryption work correctly for many RPC binding/authentication combinations by creating a secret, encrypting a string with the DCERPC transport session key, storing it through `lsa_SetSecret`, querying it back, and decrypting it.

## Important APIs, Types, and Functions

- `init_lsa_String()` initializes generated LSA string wrappers.
- `test_CreateSecret_basic()` creates an LSA secret, obtains the transport session key with `dcerpc_binding_handle_transport_session_key()`, encrypts/decrypts secret values with `sess_encrypt_string()` and `sess_decrypt_string()`, verifies corrupt encrypted data returns `NT_STATUS_UNKNOWN_REVISION`, and validates the round trip.
- `struct secret_settings` carries per-test DCERPC bind flags and NTLMSSP option toggles.
- `test_secrets()` applies settings to loadparm, connects to LSARPC, opens policy, runs the secret round-trip, and deletes the created secret when possible.
- `add_test()` builds descriptive test case names.
- `torture_rpc_lsa_secrets()` registers the full cross product of bind options and boolean auth settings.

## Control Flow

The suite constructor iterates all combinations of `keyexchange`, `ntlm2`, and `lm_key`, and for each combination adds three bind modes: big-endian push, sealed RPC, and no special bind flag. Each tcase calls `test_secrets()` with immutable settings.

`test_secrets()` writes NTLMSSP client options into the torture loadparm context, gets the base binding, applies the requested DCERPC flags, and connects to `ndr_table_lsarpc` using command-line credentials. It opens policy with the shared `test_lsa_OpenPolicy2()` helper, then calls `test_CreateSecret_basic()`.

The secret test creates a random `torturesecret-%08x` name, calls `lsa_CreateSecret`, obtains the session key, encrypts a fixed string, and stores it as the new value. It then mutates the encrypted blob and expects `lsa_SetSecret` to reject the broken value with `NT_STATUS_UNKNOWN_REVISION`. Finally it queries the secret, decrypts the returned buffer with the same session key, and checks the plaintext matches. After the test, `test_secrets()` deletes the secret object if a valid handle remains.

## State and Persistence Behavior

The file creates a live LSA secret on the target server for every test case. It attempts to delete each secret through `lsa_DeleteObject` after validation and warns rather than failing if deletion fails. Local state is transient talloc memory, RPC handles, and loadparm command-line overrides for NTLMSSP options.

## Dependencies and Integration Points

Dependencies include generated LSA RPC bindings, shared LSA policy-open helpers, command-line credentials, loadparm/cmdline configuration, DCERPC binding flag manipulation, and session-key crypto helpers from `libcli/auth`. It integrates with LSARPC policy and secret objects and requires credentials with enough access to create/query/delete secrets.

## Risks and Edge Cases

The test changes global-ish loadparm settings inside the torture context for each case, so ordering matters if future tests reuse the same context without resetting those values. Secret names use `random()` and can theoretically collide. If deletion fails, secrets persist on the server and only a warning is emitted. Some auth combinations may not be accepted by hardened servers, making failures policy-dependent rather than purely functional.

## Test Signals

The strongest signal is successful secret round-trip equality across bind/auth combinations. The corrupt encrypted blob must fail with `NT_STATUS_UNKNOWN_REVISION`; if it succeeds, the server accepted invalid secret crypto framing. Connection/open failures indicate unsupported auth options, missing privileges, or transport-session-key regressions.
