# sources/user-network-fs/impacket/impacket/eap.py

## Purpose

`eap.py` defines minimal Extensible Authentication Protocol and EAP-over-LAN packet classes for Impacket. It supplies field descriptors for EAP Expanded data, EAP request/response payload type, generic EAP headers, and 802.1X EAPOL headers.

## Important APIs, Types, And Functions

The module exports `DOT1X_AUTHENTICATION = 0x888E`, the Ethernet type for 802.1X authentication. `EAPExpanded` models RFC 3748 expanded type data with constants for WFA SMI and Simple Config, a seven-byte header, a three-byte big-endian `vendor_id`, and a big-endian `vendor_type`. `EAPR` represents EAP request/response payloads and defines `IDENTITY` and `EXPANDED` type constants with a one-byte `type` field. `EAP` defines codes for request, response, success, and failure plus `code`, `identifier`, and big-endian `length` fields. `EAPOL` defines packet types for EAP packet, start, logoff, key, and ASF alert, the default dot1x version, and fields for version, packet type, and body length.

## Control Flow

There are no custom methods. Each class inherits descriptor behavior from `impacket.helper.ProtocolPacket`; the class attributes `header_size`, `tail_size`, and field descriptors determine how packet bytes are read and written. Consumers instantiate the relevant class with or without bytes, use generated descriptor accessors/assignment behavior from `helper`, and compose bodies manually or through surrounding packet layers.

## State And Persistence

State is limited to packet instance buffers managed by `ProtocolPacket`. No authentication state machine, retransmission state, key handling, or persistence is implemented.

## Dependencies And Integration Points

The module depends on `impacket.helper.ProtocolPacket` and primitive descriptors `Byte`, `Word`, `Long`, and `ThreeBytesBigEndian`. It integrates with Ethernet/802.11 decoders or packet builders that need to represent EAPOL and EAP headers, including WPS-style expanded EAP data.

## Risks And Edge Cases

The file is intentionally minimal: it does not validate that `EAP.length` or `EAPOL.body_length` matches the actual body, does not parse EAP method-specific payloads beyond request/response type and expanded vendor/type fields, and does not implement EAPOL-Key details. Incorrect composition can therefore produce structurally inconsistent packets without local errors.

## Test Signals

Tests should verify descriptor offsets and endianness for `EAP`, `EAPR`, `EAPExpanded`, and `EAPOL`, constants for EAP/EAPOL codes, and packet composition with body lengths set by callers. Integration tests can decode known EAPOL-Start, EAP-Request/Identity, EAP-Success, and WPS expanded EAP frames.
