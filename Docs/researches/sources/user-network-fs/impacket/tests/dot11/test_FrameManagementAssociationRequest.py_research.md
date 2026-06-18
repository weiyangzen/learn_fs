# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationRequest.py

Purpose: Validates parsing and editing of 802.11 association request frames from a captured RadioTap sample.

Important APIs, types, and functions: Uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_ASSOCIATION_REQUEST`, `Dot11ManagementFrame` duration/address/sequence methods, and `Dot11ManagementAssociationRequest` capability, listen interval, SSID, supported rates, RSN, and vendor-specific methods.

Control flow: `setUp` decodes a raw frame and asserts each child class in the decoder chain before tests operate on the base and association request body. Individual tests mutate fields, then assert updated values and dynamic header-size effects.

State and persistence behavior: Packet state is entirely in memory. RSN, SSID, supported-rates, and vendor-specific setters rewrite variable-length body regions and update packet length calculations.

Dependencies and integration points: Connects RadioTap decoding to management subtype dispatch and exercises WPA/RSN information element handling.

Risks: Header-length regressions are likely if information-element insertion/removal miscomputes offsets. The test also guards 4-bit fragment and 12-bit sequence-number masking.

Test signals: Covers fixed association request fields, selected IE parsing, human-readable rate conversion, RSN replacement, and vendor IE append ordering.
