# sources/user-network-fs/impacket/tests/dcerpc/test_mgmt.py

Purpose: tests RPC Management interface calls over endpoint mapper transports.

Important APIs and functions: `MGMTTests` binds `mgmt.MSRPC_UUID_MGMT` and covers raw/helper `inq_if_ids`, `inq_stats`, `is_server_listening`, `stop_server_listening`, and `inq_princ_name`.

Control flow: each test connects to either SMB `\pipe\epmapper` or TCP port 135, builds a management request or calls the helper, and dumps the response. Stop-listening tests assert `rpc_s_access_denied`. Some calls disable automatic error checking to inspect returned management status.

State and persistence behavior: read-only except `stop_server_listening`, which would be disruptive but is expected to be denied.

Dependencies and integration points: depends on endpoint mapper service, RPC management interface, Impacket `mgmt` helpers, and the shared DCE/RPC test base.

Risks: management availability and principal-name behavior can differ by transport and security policy. Stop-listening is correctly guarded by expected denial but should not be run with privileges that could actually stop a service.

Test signals: verifies management interface binding, interface-vector parsing, stats arrays, listening status, denial handling, principal-name response handling, and SMB/TCP plus NDR/NDR64 coverage.
