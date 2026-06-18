# sources/user-network-fs/impacket/tests/SMB_RPC/test_rpcrt.py

## Purpose

`test_rpcrt.py` is a remote integration matrix for Impacket's DCE/RPC runtime engine across TCP and SMB named-pipe transports. It verifies connection setup, credential propagation, NTLM and Kerberos authentication, hash and AES key authentication, transport and DCE fragmentation, packet integrity, packet privacy, anonymous behavior, and large-request fragmentation.

## Important APIs, Types, and Functions

The core class is `RPCRTTests(RemoteTestCase)`, with concrete `RPCRTTestsTCPTransport` and `RPCRTTestsSMBTransport` subclasses marked remote. The central helper `connectDCE()` creates a transport from `self.stringBinding`, sets credentials and Kerberos state when supported, sets transport and DCE fragment sizes, sets remote name/host, obtains a DCE object, optionally propagates credentials to DCE auth, connects, sets auth type and level, and binds to the requested interface.

The suite uses `transport.DCERPCTransportFactory`, `epm.hept_lookup`, `epm.ept_lookup`, endpoint mapper UUIDs, SAMR calls, `NDRCALL`, `RPC_UNICODE_STRING`, and RPC auth constants including `RPC_C_AUTHN_WINNT`, `RPC_C_AUTHN_GSS_NEGOTIATE`, `RPC_C_AUTHN_LEVEL_NONE`, `RPC_C_AUTHN_LEVEL_PKT_INTEGRITY`, and `RPC_C_AUTHN_LEVEL_PKT_PRIVACY`.

## Control Flow

Most tests call `connectDCE()` with a particular credential/auth combination, build an endpoint mapper lookup request, send one or two `dce.request()` calls, optionally dump the response, and disconnect. The matrix covers password, LM/NT hash, Kerberos password, Kerberos hash, AES128, AES256, packet integrity, packet privacy, and fragment-size settings.

`test_bigRequestMustFragment` maps SAMR over TCP, binds with Kerberos packet privacy, sends `SamrConnect`, enumerates domains, then sends an intentionally large `SamrLookupDomainInSamServer` name to force fragmentation. It treats `STATUS_NO_SUCH_DOMAIN` as expected after the transport-level behavior succeeds. Anonymous packet integrity/privacy tests tolerate `STATUS_ACCESS_DENIED` only for SMB named-pipe bindings.

## State and Persistence Behavior

The tests are live remote tests and depend on `RemoteTestCase` fields for target, credentials, hashes, AES keys, server name, and domain. `connectDCE()` mutates transport and DCE authentication state. `test_bigRequestMustFragment` temporarily replaces `self.stringBinding` with a SAMR binding and restores it before continuing. No local files are written, and remote state is limited to reads/queries against endpoint mapper and SAMR.

## Dependencies and Integration Points

This module is one of the strongest integration tests for `impacket.dcerpc.v5.rpcrt`, transport factories, SMB named-pipe transport, TCP transport, SPNEGO/NTLM/Kerberos authentication, fragmentation, sealing/signing, and endpoint-specific NDR calls. It also depends on remote infrastructure that supports the tested protocols and credentials.

## Risks and Edge Cases

The matrix is environment-sensitive: unsupported dialects, missing AES keys, Kerberos/SPN configuration, firewalls, endpoint availability, or target policy can cause failures unrelated to code regressions. Packet privacy/integrity failures may appear only on the second request because sequence numbers and verifier state advance. Fragmentation tests deliberately use tiny fragment sizes and large SAMR names to exercise boundary behavior. Anonymous access behavior differs between TCP and named-pipe transports, and the test encodes that distinction.

## Test Signals

Passing signals indicate that DCE bind, auth negotiation, signing/sealing, request sequencing, fragmentation, and disconnect paths work across `ncacn_ip_tcp` and `ncacn_np`. This file is critical after changes to `rpcrt.py`, transport credential handling, Kerberos/NTLM auth providers, packet privacy/integrity implementation, or DCE fragmentation logic.
