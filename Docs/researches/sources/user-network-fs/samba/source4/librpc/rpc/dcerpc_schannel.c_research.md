# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_schannel.c

## Purpose

`dcerpc_schannel.c` establishes Netlogon secure-channel credentials and then binds a DCE/RPC pipe using schannel or Kerberos Netlogon authentication. It is security-critical code for machine-account authentication, secure channel negotiation, and downgrade detection.

## Important APIs, Types, and Functions

`struct schannel_key_state` tracks the secondary netlogon pipe, negotiated flags, challenges, credential material, and Kerberos authenticate request state. `struct auth_schannel_state` tracks the final bind and LogonGetCapabilities verification. The public entry points are `dcerpc_bind_auth_schannel_send()` and `dcerpc_bind_auth_schannel_recv()`. Internal stages include `dcerpc_schannel_key_send/recv()`, `continue_epm_map_binding()`, `continue_secondary_connection()`, `continue_bind_auth_krb5()`, `start_srv_challenge()`, `continue_srv_auth2()`, `continue_get_negotiated_capabilities()`, `continue_get_client_capabilities()`, and `continue_logon_control_do()`.

## Control Flow

The key setup path derives required/local negotiate flags from binding flags and loadparm policy, endpoint-maps the Netlogon interface, opens a secondary pipe, and binds either with Kerberos or no auth. Kerberos-capable paths call `netr_ServerAuthenticateKerberos`; fallback paths call `netr_ServerReqChallenge` followed by `netr_ServerAuthenticate2`. After a successful key exchange, the outer schannel bind stores the netlogon creds on `cli_credentials`, binds the requested interface, and for Netlogon pipes verifies server and client capabilities with `netr_LogonGetCapabilities`, using `netr_LogonControl` as a fallback consistency check for older or patched/unpatched behavior.

## State and Persistence Behavior

The file mutates in-memory `cli_credentials` by installing `netlogon_creds_CredentialState`. It adjusts connection flags such as `DCERPC_SEAL` and schannel/Kerberos flags. It does not persist secrets to disk; machine password material is read from credentials and used to derive credential state. Capability and authenticator state is copied and advanced carefully to keep sequence numbers synchronized.

## Dependencies and Integration Points

Dependencies include generated Netlogon client stubs, libcli auth netlogon credential helpers, credentials, GENSEC settings, loadparm crypto policy, endpoint mapper helpers, secondary connection helpers, and DCE/RPC bind-auth functions. `dcerpc_util.c` invokes this file when `DCERPC_SCHANNEL` is requested and no netlogon creds are already cached.

## Risks and Test Signals

Risks are downgrade acceptance, policy drift around AES/MD5/strong-key requirements, Kerberos Netlogon feature availability, secondary-pipe lifecycle errors, and sequence-number desynchronization in fallback probes. Test signals include schannel with AES, strong-key-only, MD5-rejected, Kerberos Netlogon enabled/disabled, RODC channel type, legacy NT/Samba servers, tampered capability replies, and authentication retry after server `ACCESS_DENIED`.
