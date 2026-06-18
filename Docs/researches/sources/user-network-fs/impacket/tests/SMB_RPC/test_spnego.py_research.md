# sources/user-network-fs/impacket/tests/SMB_RPC/test_spnego.py

## Purpose

`test_spnego.py` is a compact local golden-byte suite for SPNEGO token parsing and packing in `impacket.smb`. It verifies `NegTokenInit` and `NegTokenResp` round trips for NTLMSSP negotiation payloads and explicit construction of a request-MIC response.

## Important APIs, Types, and Functions

The file defines one `unittest.TestCase` class named `Test`. `setUp()` stores six DER/ASN.1 SPNEGO byte strings: two `negTokenInit` values, three response values, and one constructed request-MIC response. Test methods use `smb.SPNEGO_NegTokenInit`, `smb.SPNEGO_NegTokenResp`, and `smb.TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']`.

## Control Flow

Five tests instantiate the appropriate SPNEGO token class, parse a stored byte string with `fromString()`, and assert that `getData()` returns the original bytes. `test_negTokenResp4` constructs a response by assigning `NegState` to `b'\x03'` and `SupportedMech` to the NTLMSSP mechanism OID, then asserts the packed output matches the stored DER bytes.

## State and Persistence Behavior

All state is local to the test instance and token objects. There is no network, filesystem, or global module mutation. The byte fixtures include embedded NTLMSSP negotiate/challenge/authenticate payloads but are treated as opaque SPNEGO token data.

## Dependencies and Integration Points

The suite depends only on `unittest` and `impacket.smb`. It integrates with SMB authentication because the SPNEGO helpers are used around NTLMSSP messages during extended-security negotiation. It also indirectly guards Impacket's ASN.1 length encoding for short and long-form SPNEGO structures.

## Risks and Edge Cases

Coverage is intentionally narrow but sensitive to byte-for-byte encoding. It exercises long-form lengths (`0x81`, `0x82`), optional fields, NTLMSSP mech OIDs, negState values, and response tokens with and without supported mechanism fields. The tests do not validate semantic contents of the nested NTLM messages beyond preserving the outer SPNEGO bytes.

## Test Signals

Passing tests indicate that SPNEGO token parsing is lossless for captured NTLMSSP negotiation flows and that constructing a request-MIC response emits the expected encoding. Run this file after changes to `SPNEGO_NegTokenInit`, `SPNEGO_NegTokenResp`, ASN.1 length handling, mechanism OID mapping, or SMB extended-security negotiation.
