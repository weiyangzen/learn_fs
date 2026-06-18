# sources/user-network-fs/samba/source4/librpc/idl/ntp_signd.idl

## Purpose

`ntp_signd.idl` defines the internal NTP signing protocol structures used to request, produce, and verify signed NTP packets.

## Important APIs And Types

The interface UUID is `0da00951-5b6c-4488-9a89-750cac70920c`, version 1.0. `NTP_SIGND_PROTOCOL_VERSION_0` is the fixed protocol version. `ntp_signd_op` enumerates client/server sign and check operations plus success/failure replies. `sign_request` is a big-endian public struct with protocol version, operation, packet id, little-endian key id, and remaining packet data. `signed_reply` is a big-endian public struct with version, operation, packet id, and remaining signed packet data.

## Control Flow And State

The IDL only defines serialization. Operationally, a client sends a `sign_request` with a packet to sign or verify, and the responder returns `signed_reply` with success/failure semantics encoded in `op` and the signed packet payload.

## Dependencies And Integration Points

The generated NDR parser is built by the IDL Waf script. It relies on `DATA_BLOB` and NDR endian flags from Samba IDL support. It is used by NTP signing components that need byte-accurate packet preservation.

## Risks

The mixed endian annotations are security-sensitive: protocol fields are big-endian except `key_id`, which is explicitly little-endian. Any parser change can break interoperability or signature verification. `NDR_REMAINING` payloads require callers to enforce packet length expectations.

## Test Signals

Tests should round-trip known sign requests/replies, verify `key_id` endian behavior, and reject malformed or truncated remaining payloads.
