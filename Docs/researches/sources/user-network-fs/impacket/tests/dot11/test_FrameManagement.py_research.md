# sources/user-network-fs/impacket/tests/dot11/test_FrameManagement.py

Purpose: Exercises Impacket's 802.11 beacon management-frame decoding and mutation path from a complete RadioTap capture.

Important APIs, types, and functions: `TestDot11ManagementBeaconFrames` uses `RadioTapDecoder.decode`, `Dot11Types` constants, `Dot11.get_type`, `get_subtype`, `get_type_n_subtype`, `Dot11ManagementFrame` address/sequence helpers, and `Dot11ManagementBeacon` timestamp, beacon interval, capability, SSID, supported-rates, DS parameter, and vendor-specific IE helpers.

Control flow: `setUp` decodes a raw RadioTap frame, walks `radiotap.child()` to `Dot11`, then to the management base and beacon body. Tests validate fixed fields first, then mutate variable tagged parameters and check resulting header-size changes.

State and persistence behavior: All state is in packet objects built from in-memory bytes; setters mutate the packet buffer and derived length metadata. No filesystem or network persistence occurs.

Dependencies and integration points: Integrates `impacket.ImpactDecoder.RadioTapDecoder` with `impacket.dot11` packet classes and Python 2/3 class-name compatibility through `six.PY2`.

Risks: The suite is sensitive to tagged information element offsets and assumes vendor-specific IE parsing preserves ordering. Header-size assertions catch regressions where setters fail to resize packet buffers.

Test signals: Strong regression signal for beacon decoding, address mutation, sequence masking, supported-rate human-readable conversion, and vendor IE append behavior.
