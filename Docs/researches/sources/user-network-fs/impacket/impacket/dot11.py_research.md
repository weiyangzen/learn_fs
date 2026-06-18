# sources/user-network-fs/impacket/impacket/dot11.py

## Purpose

`dot11.py` is Impacket's 802.11 packet model. It covers frame-control bit access, control/data/management frame layouts, LLC/SNAP encapsulation, WEP/WPA/WPA2 security headers and trailers, radiotap capture metadata, and management information elements for beacons, probes, authentication, deauthentication, association, and reassociation.

## Important APIs, Types, And Functions

`Dot11ManagementCapabilities`, `Dot11Types`, `SAPTypes`, `DOT11_MANAGEMENT_ELEMENTS`, `DOT11_REASON_CODES`, `DOT11_AUTH_ALGORITHMS`, and `DOT11_AUTH_STATUS_CODES` are constant namespaces. `Dot11` exposes frame-control getters/setters for protocol version, type, subtype, ToDS/FromDS, retry, power management, protected frame, order, QoS/no-body/CF flags, and optional FCS calculation. Control frame classes (`Dot11ControlFrameCTS`, `ACK`, `RTS`, `PSPoll`, `CFEnd`, `CFEndCFACK`) expose duration and address/AID fields. Data frame classes (`Dot11DataFrame`, `Dot11DataQoSFrame`, `Dot11DataAddr4Frame`, `Dot11DataAddr4QoSFrame`) expose addresses, sequence/fragment fields, QoS, and body access.

`LLC` and `SNAP` model 802.2/SNAP headers. `Dot11WEP`, `Dot11WEPData`, `Dot11WPA`, `Dot11WPAData`, `Dot11WPA2`, and `Dot11WPA2Data` model security metadata. WEP supports RC4 encrypt/decrypt using IV plus caller-supplied key and ICV CRC checks; WPA/WPA2 mostly expose TSC/PN/keyid/extIV and MIC/ICV trailer fields.

`RadioTap` dynamically manages present-bit fields and aligned values for TSFT, flags, rate, channel, FHSS, signal/noise, lock quality, TX power/flags, FCS-in-header, retries, and xchannel. Management classes include `Dot11ManagementFrame`, the generic `Dot11ManagementHelper`, and specialized beacon, probe request/response, deauthentication/disassociation, authentication, association request/response, and reassociation request/response classes.

## Control Flow

Most classes follow the `ProtocolPacket` pattern: choose fixed header/tail sizes in `__init__()`, load an optional buffer, then expose byte/word-level getters and setters. `Dot11` manages the initial two-byte frame-control field and optional four-byte FCS tail. Data and control subclasses map offsets directly to fields. WEP encryption builds an RC4 key from three IV bytes plus the secret key and decrypts/encrypts the body symmetrically; WEP data computes CRC32 over the body for ICV.

`RadioTap` has the most complex flow. It keeps a sorted list of field descriptors, checks present bits, walks extended present maps, aligns offsets according to each field's alignment, inserts/removes packed field bytes, and updates the radiotap length field before emitting a packet. Management helper flow parses a tail of information elements as `(id, length, data)` triples; `_get_element()` and `_get_elements_generator()` scan the body, `_set_element()` replaces or appends elements while preserving fixed header and tail, and `delete_element()` removes one or many elements. Specialized management classes add semantic wrappers for SSID, supported rates, DS channel, RSN, ERP, country, vendor-specific IEs, challenge text, auth status, reason code, and association fields.

## State And Persistence

There is no persistence beyond packet buffers. Each instance stores header/body/tail bytes in `ProtocolPacket`; mutators rewrite those buffers. `RadioTap` recalculates its length from the current header. Management element helpers recalculate body length when elements are changed. Cryptographic methods do not store keys or decrypted state.

## Dependencies And Integration Points

The module depends on Python `struct`, `binascii.crc32`, `ImpactPacket.ProtocolPacket`, `array_tobytes`, and `Dot11Crypto.RC4`. It is typically consumed by capture decoders, packet crafting tools, wireless tests, and higher-level decoders that choose subclasses based on `Dot11Types` type/subtype values. Radiotap support integrates with monitor-mode capture/injection metadata.

## Risks And Edge Cases

The module trusts buffer lengths heavily; many setters index fixed six-byte addresses without validation, and parsers can raise low-level exceptions on truncated frames. Several security helpers are classifiers/field wrappers rather than full WPA/WPA2 cryptographic implementations; `get_decrypted_data()` for WPA/WPA2 returns raw body data with TODO comments. `set_MIC()` calls `value.ljust()` without assigning the result, so short values may not actually be padded before slicing. Some radiotap field definitions intentionally clash with historical alternatives, and `set_hardware_queue()` references a commented-out descriptor, so that method can fail. Management vendor-specific parsing contains a Spanish exception string and assumes generated elements never return `None`. FCS/ICV endian conversions need fixture coverage because CRC32 byte order is handled manually.

## Test Signals

Tests should verify bit-level frame-control setters, control/data frame address offsets, sequence and fragment masking, WEP IV/keyid/ICV and RC4 round trips, WPA/WPA2 PN/TSC classification, LLC/SNAP OUI/PID handling, radiotap insertion/removal/alignment/length updates, and management IE add/get/delete for SSID, rates, DS channel, RSN, country, ERP, and multiple vendor-specific IEs. Fuzzing truncated management and radiotap buffers would be valuable because parsing is offset-heavy.
