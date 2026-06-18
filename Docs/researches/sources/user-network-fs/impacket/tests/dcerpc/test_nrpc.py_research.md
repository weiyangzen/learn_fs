# sources/user-network-fs/impacket/tests/dcerpc/test_nrpc.py

Purpose: extensive Netlogon Remote Protocol (`nrpc`) coverage for domain controller discovery, site/trust queries, secure-channel challenge/authentication, logon validation, database sync calls, and control APIs.

Important APIs and functions: `NRPCTests` uses `nrpc.MSRPC_UUID_NRPC`, `authn=True`, and `machine_account=True`. `authenticate()` performs `hNetrServerReqChallenge`, computes a strong session key with the machine account NT hash, computes the client credential, and calls `hNetrServerAuthenticate3`. `update_authenticator()` returns a Netlogon authenticator from the stored credential/session key. Tests cover many raw/helper `Dsr*`, `Netr*`, trust, digest, control, and UAS operations.

Control flow: discovery tests issue unauthenticated/authenticated Netlogon location and site requests. Secure-channel tests explicitly build challenge/authenticate requests for Authenticate, Authenticate2, and Authenticate3. Xfailed privileged tests call `authenticate()` before password, domain info, capability, database sync, forest trust, trust info, and send-to-SAM paths. SamLogon tests encrypt LM/NT OWF password values with RC4 over the session key and submit interactive logon structures.

State and persistence behavior: most operations are read/query or expected access-denied. Password-set and database-sync paths are xfailed and expected to fail; if they unexpectedly ran with privilege they could be sensitive. `DsrDeregisterDnsHostRecords`, service bits, controls, and send-to-SAM are also sensitive but coded to expect denial/not-supported. No cleanup is needed for successful read-only calls.

Dependencies and integration points: depends on machine-account credentials from remote config, Netlogon named pipe or endpoint-mapped TCP, `ntlm` hash functions, optional `Cryptodome.Cipher.ARC4`, and modern domain controller Netlogon hardening behavior.

Risks: many assertions are environment-specific expected errors (`STATUS_DOWNGRADE_DETECTED`, `STATUS_NOT_SUPPORTED`, `rpc_s_access_denied`, `ERROR_NO_SUCH_DOMAIN`). The TODO notes that secure RPC session establishment is incomplete, and Zerologon patching causes xfails. Machine account hash handling is sensitive. Some calls use hardcoded test strings and RIDs.

Test signals: verifies Netlogon structure marshalling, challenge/credential computation, helper parity, domain/site/trust discovery, expected post-hardening failures, encrypted SamLogon payload construction, and transport coverage over SMB and TCP.
