# sources/user-network-fs/impacket/examples/rdp_check.py

## Purpose

`rdp_check.py` is a partial RDPBCGR/CredSSP client used to validate whether supplied NTLM credentials are accepted by an RDP endpoint. It hand-builds the TPKT/TPDU negotiation, upgrades to TLS, performs an NTLM SPNEGO exchange inside CredSSP `TSRequest` messages, and reports access granted or denied without establishing a full RDP session.

## Important APIs, Types, and Functions

The packet structures are `TPKT`, `TPDU`, `CR_TPDU`, `DATA_TPDU`, `RDP_NEG_REQ`, `RDP_NEG_RSP`, and `RDP_NEG_FAILURE`, all using Impacket `Structure`. CredSSP ASN.1 payloads are modeled by `TSPasswordCreds`, `TSCredentials`, and `TSRequest` subclasses of `GSSAPI`. Runtime-only `SPNEGOCipher` wraps NTLM signing/sealing state. `check_rdp()` drives negotiation, TLS setup, NTLM type 1/type 3 creation, public key sealing, credential sealing, and result logging.

## Control Flow

The CLI parses `[[domain/]user[:pass]@]target`, optional hashes, IPv6, and logging flags. `check_rdp()` sends an RDP negotiation request for SSL plus hybrid CredSSP, rejects servers that do not support hybrid mode, starts a pyOpenSSL TLS session, sends NTLM type 1 in `TSRequest.NegoData`, parses the server challenge, computes NTLM type 3 with password or hashes, extracts the server certificate public key, seals it into `pubKeyAuth`, and sends the final auth token. It then parses the server `pubKeyAuth`, seals `TSCredentials`, sends them as `authInfo`, closes TLS, and logs success if the preceding exchange did not raise an access-denied exception.

## State and Persistence Behavior

The script opens a TCP connection to port 3389 and mutates only in-memory protocol state. It does not create files or persistent remote state. The target receives a real CredSSP authentication attempt, so account lockout and audit records are possible. Passwords and NTLM hashes are kept in process memory.

## Dependencies and Integration Points

It depends on `get_connected_socket`, `parse_target`, Impacket `ntlm`, ASN.1 helpers from `impacket.spnego`, `Cryptodome.Cipher.ARC4`, and pyOpenSSL `SSL`/`crypto`. It integrates directly with RDP servers that support CredSSP hybrid security and with Impacket's example logger.

## Risks and Edge Cases

The implementation intentionally shortcuts full CredSSP verification and notes incomplete signature validation. TLS is configured with `ALL:@SECLEVEL=0` and unsafe legacy renegotiation compatibility, which broadens protocol compatibility at security cost. Hash parsing requires `LMHASH:NTHASH`. Socket/TLS reads have fixed buffer sizes and limited recovery behavior. Authentication attempts can trigger lockouts, and the "access granted" inference relies on observed protocol behavior rather than a complete RDP login.

## Test Signals

Unit tests should round-trip `TSRequest`, `TSPasswordCreds`, and `TSCredentials` encoding/decoding and mock NTLM sealing. Integration tests need Windows RDP targets with valid, invalid, hash-based, and IPv6 authentication cases, plus a non-CredSSP server path that should log unsupported hybrid security.
