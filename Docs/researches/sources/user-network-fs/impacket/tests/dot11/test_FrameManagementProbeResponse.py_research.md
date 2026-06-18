# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeResponse.py

Purpose: Exercises probe response decoding, beacon-like fixed fields, and large vendor-specific IE lists including WPS/WPA data.

Important APIs, types, and functions: Uses `Dot11ManagementProbeResponse` timestamp, beacon interval, capabilities, SSID, supported-rates, DS parameter, and vendor-specific helpers with `RadioTapDecoder` and `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_PROBE_RESPONSE`.

Control flow: Setup decodes a large raw RadioTap probe response and asserts class dispatch. Tests verify base fields, fixed beacon-compatible fields, variable IEs, and appending a new vendor-specific element.

State and persistence behavior: State is packet-local. Variable IE operations mutate the backing bytes and update header-size calculations.

Dependencies and integration points: Integrates management parsing with WPS and WPA vendor IE tuple extraction, preserving multiple OUIs in order.

Risks: The large frame body makes offset drift likely when one IE is resized. Vendor-specific parsing must handle multiple entries with the same OUI and different payload lengths.

Test signals: Strong signal for probe-response body parsing, timestamp endian handling, DS channel, rate conversion, vendor IE enumeration, and appended IE size accounting.
