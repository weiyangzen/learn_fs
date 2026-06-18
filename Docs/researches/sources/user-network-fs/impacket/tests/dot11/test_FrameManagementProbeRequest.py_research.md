# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeRequest.py

Purpose: Tests probe request management-frame decoding and variable information element mutation.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_PROBE_REQUEST`, `Dot11ManagementProbeRequest.get/set_ssid`, `get/set_supported_rates`, and common `Dot11ManagementFrame` fixed-field helpers.

Control flow: Setup decodes a raw probe request through RadioTap and Dot11 layers, then tests header sizes, base-frame fields, raw body bytes, SSID replacement, and supported-rate replacement.

State and persistence behavior: No external state. SSID and rate setters mutate variable-length IE content and update packet-size accounting in memory.

Dependencies and integration points: Exercises RadioTap-to-Dot11 management subtype dispatch and tagged IE parsing for client-originated probe requests.

Risks: Probe requests often contain short variable sections; length changes can shift all later IEs. Header-size assertions specifically guard those offset calculations.

Test signals: Validates broadcast destination/BSSID handling, source address extraction, sequence masking, SSID parsing, supported-rate tuple conversion, and dynamic header-size recalculation.
