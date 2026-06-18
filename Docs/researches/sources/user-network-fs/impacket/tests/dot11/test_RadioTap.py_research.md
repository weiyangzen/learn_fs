# sources/user-network-fs/impacket/tests/dot11/test_RadioTap.py

Purpose: Provides broad regression coverage for the `RadioTap` packet class: present flags, optional field accessors, field insertion/removal, serialization, and extended present flags.

Important APIs, types, and functions: Uses `RadioTap` constants such as `RTF_TSFT`, `RTF_FLAGS`, `RTF_CHANNEL`, `RTF_EXT`; getters/setters for TSFT, flags, rate, channel, FHSS, antenna signal/noise, lock quality, attenuation, TX power, antenna, FCS, retries, TX flags, xchannel, and `get_packet`; also uses `ImpactPacket.Data`.

Control flow: `setUp` builds four representative RadioTap frames with different present bit layouts. Tests read existing fields, insert absent fields, unset fields, serialize fresh RadioTap objects, and validate extended present-bit parsing.

State and persistence behavior: RadioTap instances mutate in memory. Setters modify present flags, byte layout, header length, and total size; no external persistence.

Dependencies and integration points: Core integration point for all RadioTap decoder tests and Dot11 frame decoding; payload containment is checked with `Data`.

Risks: Optional-field ordering and alignment are high-risk because adding/removing one field shifts later field offsets. Extended present words are also error-prone.

Test signals: Strong signal across field presence bits, dynamic length updates, serialization defaults, payload containment, and extended-present interpretation.
