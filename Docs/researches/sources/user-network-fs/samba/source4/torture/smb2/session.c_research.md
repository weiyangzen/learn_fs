# sources/user-network-fs/samba/source4/torture/smb2/session.c

## Purpose

`session.c` is the SMB2 torture suite for session setup, reauthentication, Kerberos ticket expiry, multichannel session binding, signing/encryption negotiation, anonymous session edge cases, and targeted session regressions. It is client-side test code: it opens SMB2 trees, mutates client/session state, sends SMB2 requests, and asserts server status codes and connection state. Its exported integration points are `torture_smb2_session_init()` and `torture_smb2_session_req_sign_init()`, which register many named tests into the `smb2.session` and `smb2.session-require-signing` suites.

## Important APIs, Types, and Functions

The file is built around Samba torture and SMB2 client APIs: `struct torture_context`, `struct smb2_tree`, `struct smb2_session`, `struct smb2_transport`, `struct smbcli_options`, `struct cli_credentials`, `struct smb2_create`, `union smb_fileinfo`, and `union smb_setfileinfo`. It uses `smb2_connect()`, `torture_smb2_connection_ext()`, `torture_smb2_session_setup()`, `smb2_session_setup_spnego()`, `smb2_session_channel()`, `smb2_session_init()`, `smb2_tree_init()`, `smb2cli_tcon_send()/recv()`, `smb2cli_session_current_id()`, `smb2cli_session_set_id_and_flags()`, `smb2cli_session_encryption_on()`, `smb2cli_tcon_is_encryption_on()`, `smb2cli_conn_server_capabilities()`, `smb2cli_conn_server_signing_algo()`, `smbXcli_conn_disconnect()`, and `smbXcli_conn_is_connected()`.

`CHECK_CREATED` validates create responses and `WAIT_FOR_ASYNC_RESPONSE` drives tevent until an async request is cancellable or no longer receiving. `sleep_remaining()` sleeps until a calculated Kerberos-expiry time. The constants `KRB5_TICKET_LIFETIME`, `KRB5_CLOCKSKEW`, and `GENSEC_GSSAPI_REQUESTED_LIFETIME()` force short-lived GSSAPI credentials for expiry tests.

Core test families:

- `test_session_reconnect1/2()` validate reconnect behavior with previous session ids and old-handle invalidation.
- `test_session_reauth1` through `test_session_reauth6()` validate same-session reauth, anonymous reauth, security descriptor access, rename authorization after reauth, and failed reauth session teardown.
- `test_session_expire1i()`, `test_session_expire2i()`, and wrappers exercise Kerberos expiry under normal, signed, and encrypted operation.
- `test_session_bind1()`, `test_session_bind2()`, `test_session_bind_auth_mismatch()`, and the many `test_session_bind_negative_*()` functions cover multichannel binding and dialect/signing/encryption capability mismatches.
- `test_session_sign_enc()` plus signing/encryption wrappers validates negotiated algorithms against normal IO and async notify cancellation.
- Anonymous tests manipulate `anonymous_session_key`, forced session keys, encryption/signing torture knobs, and IPC tree connect behavior.
- `test_session_ntlmssp_bug14932()` and `test_session_require_sign_bug15397()` cover specific regressions.

## Control Flow

Most tests follow the same pattern: build a random file name, clean it with `smb2_util_unlink()`, create it through `smb2_create()`, assert the create action/oplock/attributes, perform a session operation, then verify follow-up SMB2 calls return exactly the expected `NTSTATUS`. Cleanup closes handles, deletes created files or trees, frees talloc parents, and restores altered config such as the requested GSSAPI lifetime.

Reconnect tests capture the current session id and reconnect with that id. They then verify old handles on the old session return `NT_STATUS_USER_SESSION_DELETED`, while new or rebound sessions can reopen or clean up state. Reauth tests call `smb2_session_setup_spnego()` on an existing session with original, anonymous, or deliberately corrupted credentials, then test whether file handles and security descriptors still behave as expected.

Expiry tests require `--use-kerberos=required`. They invalidate the credential cache, request a five-second ticket lifetime, sleep past the expiry window, then assert that most session-bound operations fail with `NT_STATUS_NETWORK_SESSION_EXPIRED`. `test_session_expire2i()` is a broad matrix over getinfo, setinfo, flush, read, write, ioctl, oplock/lease ack, directory find, compound create/find/close, notify cancellation, tree connect, root handle create, tree disconnect, unlock, close, echo, and logoff. Its important distinction is that unlock, close, echo, and logoff are still allowed after expiry, while normal file and tree operations are not.

Multichannel tests first check `SMB2_CAP_MULTI_CHANNEL` and then build multiple transports with controlled `client_guid`, protocol range, signing, encryption, and `only_negprot` settings. Positive bind tests verify one session can be used over another transport. Negative bind tests call the shared `test_session_bind_negative_smbXtoX()` helper to attempt invalid binds, check exact rejection status, check behavior when the bind flag or session keys are missing, and ensure the original session remains usable. The large matrix intentionally varies SMB 2.02, SMB 2.10, SMB 3.x, SMB 3.1.1 signing algorithms, encryption algorithms, same/different client GUIDs, and required encryption state.

Signing/encryption algorithm tests use a helper that connects with a narrow algorithm list, creates a file, issues a pending notify, cancels it, and verifies the session still works. Anonymous security tests force anonymous session-key behavior and verify whether encrypted or signed IPC tree connects are accepted, reset, or access-denied depending on the key and signing setup.

## State and Persistence Behavior

This file creates temporary files and sometimes directories on the SMB share, almost always with random suffixes and often `DELETE_ON_CLOSE`. It also mutates client-side session state directly: `tree->session` is swapped among channel sessions, options structures are copied and modified, credentials are shallow-copied and altered, session ids/flags are injected, and connections are deliberately disconnected. Kerberos tests mutate global loadparm state by setting `gensec_gssapi:requested_life_time` and then reset it to `0` in cleanup. Credential caches are invalidated before and after expiry tests.

Server-visible persistent state should be limited to transient files, share handles, locks, and security descriptor changes during test execution. Cleanup paths unlink files, close handles, delete trees, and free talloc contexts. Risks remain where assertion jumps skip some disconnect cleanup or where helper tests free the incoming `tree0`/`tree1`, which is expected by the wrapper but important for callers.

## Dependencies and Integration Points

The file depends on Samba SMB2 client calls (`libcli/smb2`), low-level `smbXcli` session/transport primitives, torture assertions, credentials and Kerberos support, security descriptor manipulation, tevent async handling, resolver/loadparm config, and NT status helpers. It integrates with `smb2.c` through `torture_smb2_session_init()` and `torture_smb2_session_req_sign_init()`. Tests require a configured host/share, valid credentials, sometimes `user2` credentials, Kerberos infrastructure, SMB3/multichannel support, SMB 3.1.1 algorithm negotiation support, and server capabilities such as leasing or encryption depending on the case.

## Risks

The main risk is brittleness from timing and environment: the Kerberos expiry tests rely on a five-second ticket lifetime plus skew and can fail on slow systems, clock skew, KDC behavior, or credential-cache quirks. The multichannel and algorithm tests are capability-sensitive and intentionally skip when the negotiated protocol or server feature set is insufficient. The code also reaches into session internals (`needs_bind`, forced session keys, session ids, anonymous flags), so changes to client internals can affect tests even if wire behavior is unchanged.

Because tests swap `tree->session`, deliberately disconnect transports, and free trees passed by wrappers, cleanup correctness is essential. A missed restore can make later cleanup use the wrong session or transport. Negative status expectations are protocol-contract assertions; server changes that return different but plausible errors will surface as regressions and should be checked against MS-SMB2 expectations and Samba bug references before updating tests.

## Test Signals

Strong signals are exact `NTSTATUS` assertions, connection-state checks, authenticated/anonymous state checks, create action and oplock assertions, successful post-error reuse of original sessions, and skip messages tied to missing capabilities. The suite names registered at the end map directly to runnable torture tests such as `smb2.session.reauth6`, `smb2.session.expire2e`, `smb2.session.bind_negative_smb3signGtoH2Xd`, and `smb2.session-require-signing.bug15397`.
