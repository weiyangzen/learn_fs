# sources/user-network-fs/impacket/impacket/spnego.py

## Purpose

`spnego.py` implements the SPNEGO/GSSAPI token helpers used by Impacket's SMB, SMB2/3, and DCERPC authentication paths. It provides manual ASN.1 BER length encoding/decoding, token wrappers for SPNEGO `NegTokenInit` and `NegTokenResp`, OID mappings for common negotiated mechanisms, and an NTLM-backed signing/sealing helper for SPNEGO-protected payloads.

The file is intentionally low-level: callers work with raw bytes, ASN.1 tag constants, and field dictionaries rather than a full ASN.1 schema library. Its main role is to serialize and parse the subset of SPNEGO needed to carry NTLM/Kerberos negotiation tokens and to apply NTLM session security after negotiation.

## Important APIs, Types, And Functions

`GSS_API_SPNEGO_UUID`, ASN.1 tag constants, `MechTypes`, and `TypesMech` define the object identifiers and labels that drive negotiation. `MechTypes` maps raw OID bytes to human-readable mechanism names for NTLMSSP, Microsoft Kerberos, Kerberos, Kerberos user-to-user, and NEGOEX; `TypesMech` provides the reverse lookup commonly used when constructing `MechTypes` arrays.

`asn1encode(data)` emits BER length-prefixed payloads for lengths from short form through 4-byte long form. `asn1decode(data)` reads a BER length field and returns `(payload_slice, consumed_byte_count)`. These helpers encode only lengths, not tags; callers prepend tags separately.

`GSSAPI` models the generic GSS-API initial context token wrapper. It stores fields in `self.fields`, defaults `UUID` to the SPNEGO OID, parses `ASN1_AID`/`ASN1_OID` wrappers in `fromString()`, exposes the remaining token as `Payload`, and emits the wrapper in `getData()`.

`SPNEGO_NegTokenResp` parses and builds target/client response tokens. Its fields can include `NegState`, `SupportedMech`, `ResponseToken`, and `mechListMIC`. `getData()` has separate branches for server responses with negotiation state and supported mechanism, server responses without response token, state-only responses, and client responses with or without a mechanism-list MIC.

`SPNEGO_NegTokenInit` subclasses `GSSAPI` and parses/builds the initial SPNEGO token. It extracts a list of mechanism OIDs into `MechTypes` and optionally extracts a `MechToken`. `getData()` serializes the mechanism list and optional token, stores the resulting inner token as `Payload`, then delegates to `GSSAPI.getData()`.

`SPNEGOCipher` wraps NTLM signing/sealing functions. It derives client/server signing and sealing keys with `ntlm.SIGNKEY()` and `ntlm.SEALKEY()` when extended session security is negotiated, initializes ARC4 handles, and exposes `encrypt()`, `decrypt()`, and `sign()` for SPNEGO session protection.

## Control Flow

SPNEGO token parsing is a strict tag-by-tag walk over bytes. `GSSAPI.fromString()` first validates the application identifier tag (`0x60`), decodes the wrapper length, validates the OID tag, decodes the OID, and stores all remaining bytes as the SPNEGO payload. `SPNEGO_NegTokenInit.fromString()` then validates the inner `NegTokenInit` tag, sequence tag, mechanism-list context tag, nested sequence, and each OID until a non-OID tag is reached. After the mechanism list it checks whether the remaining data starts with the mechanism-token context tag and, if so, decodes the nested octet string into `MechToken`.

`SPNEGO_NegTokenResp.fromString()` expects a response token tag, then a sequence. It first checks whether a negotiation-state field is present. If present, it decodes the enumerated value, then optionally consumes `SupportedMech`, and finally consumes `ResponseToken` if present. If the first field is already a response token, it skips state/mechanism parsing. The response token itself is expected to be an ASN.1 octet string nested inside the response-token context tag.

Serialization mirrors those fixed shapes. `SPNEGO_NegTokenInit.getData()` builds OID entries, wraps them in the mechanism-list sequence and optional mechanism token, assigns `Payload`, and relies on `GSSAPI.getData()` for the outer GSS header. `SPNEGO_NegTokenResp.getData()` chooses an ASN.1 layout from the field keys currently present; missing keys materially change the produced token shape.

`SPNEGOCipher` initializes per-direction RC4 state in the constructor. `encrypt()` seals and signs outgoing client data using the current sequence number, then increments the sequence. `decrypt()` calls `ntlm.SEAL()` against the server-side keys and handles but does not increment `__sequence`. `sign()` computes a MAC over caller-provided data and increments `__sequence`; optionally it resets both sealing handles to their initial RC4 state.

## State And Persistence Behavior

There is no disk or network persistence. Token objects keep parsed and caller-supplied values in a mutable `fields` dictionary. Re-serialization is entirely derived from current field contents except for `GSSAPI.UUID`, which defaults to the SPNEGO OID.

`SPNEGOCipher` has meaningful in-memory state. It stores negotiated flags, signing/sealing keys, RC4 encrypt-call handles for client and server directions, and a private sequence counter. The ARC4 handles are stateful stream ciphers, so call order matters. `encrypt()` and `sign()` advance `__sequence`; `decrypt()` uses the current sequence but does not advance it in this implementation, so consumers must understand expected sequencing before mixing encrypt/decrypt/sign operations.

## Dependencies And Integration Points

The module depends on Python `struct` for byte packing, `impacket.ntlm` for NTLM key derivation/MAC/sealing, and `Cryptodome.Cipher.ARC4` for RC4 stream state. It is integrated by higher-level Impacket authentication code that builds SPNEGO blobs for SMB, SMB2/3, and DCERPC, especially when transporting NTLMSSP negotiate/challenge/authenticate messages.

It also exposes OID mappings used by callers to select or display mechanisms. `TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']` is the typical path for constructing an initial mechanism list, while parsed `SupportedMech` values are raw OID bytes that can be resolved through `MechTypes`.

## Risks And Edge Cases

ASN.1 handling is handwritten and intentionally narrow. It does not implement a general BER/DER parser, indefinite lengths, high-tag-number forms, or schema-level validation. Truncated data usually fails through `struct.unpack()` or explicit tag checks rather than through structured parse errors.

`asn1decode()` has a precedence-sensitive expression in the `0x83` length branch: `data[:len2 << 16 + len3]` is parsed differently from the intended `data[:(len2 << 16) + len3]`. Very large tokens are unusual here, but that branch is a correctness risk for 3-byte BER lengths.

`GSSAPI.fromString()` stores the parsed OID as `OID` but `getData()` serializes `UUID`; parsing a non-default OID and re-emitting without copying `OID` back to `UUID` will produce the default SPNEGO OID. That is probably acceptable for this SPNEGO-specific wrapper but is a trap if reused as a generic GSS token class.

`SPNEGO_NegTokenResp.getData()` is field-presence driven. Partial field combinations outside the anticipated branches can emit a client-style response or raise `KeyError` late. The parser similarly supports only a subset of optional field orderings.

`SPNEGOCipher` relies on mutable RC4 handles and sequence counters. Reusing a cipher object across independent sessions or calling signing/decryption in an unexpected order can corrupt message protection state. The non-extended-session-security branch assigns `__clientSealingKey` twice and never separately assigns `__serverSealingKey`, although both signing and sealing keys are equivalent in that mode.

## Test Signals

Useful tests should round-trip `asn1encode()`/`asn1decode()` at boundary lengths `0x7f`, `0x80`, `0xff`, `0x100`, `0xffff`, and `0x10000`, with explicit coverage for the 3-byte length branch. Token tests should build a `SPNEGO_NegTokenInit` with NTLM and Kerberos OIDs plus a dummy mechanism token, parse it back, and verify `MechTypes`, `MechToken`, and outer GSS fields.

Response-token tests should cover server responses with `NegState` only, `NegState` plus `SupportedMech`, full server responses with `ResponseToken`, and client responses with and without `mechListMIC`. Negative tests should assert failures for wrong tags, missing nested octet strings, and truncated BER lengths.

Cipher tests should use known NTLM session security vectors or local round-trip expectations from `ntlm.SEAL()`/`ntlm.MAC()`, verify sequence increments after `encrypt()` and `sign()`, and explicitly document the expected decrypt sequence behavior.
