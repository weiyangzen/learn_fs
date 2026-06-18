# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDeauthentication.py

Purpose: Tests deauthentication management-frame parsing and reason-code mutation.

Important APIs, types, and functions: Uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_DEAUTHENTICATION`, common `Dot11ManagementFrame` field helpers, and `Dot11ManagementDeauthentication.get_reason_code` / `set_reason_code`.

Control flow: Setup decodes a compact RadioTap frame to `Dot11ManagementDeauthentication`. Tests assert header sizes, fixed base fields, frame body bytes, sequence/fragment masking, and the two-byte reason code.

State and persistence behavior: Mutates in-memory packet bytes only. No external state is read beyond the raw literal frame.

Dependencies and integration points: Integrates management subtype dispatch with the common deauth/disassoc reason-code packet shape.

Risks: The class name in this file is still `TestDot11ManagementBeaconFrames`, so test discovery relies on method naming rather than semantic class naming. Reason-code parsing is tiny, making offset mistakes the main implementation risk.

Test signals: Covers subtype dispatch, address/sequence operations, exact body extraction, and reason-code setter/getter behavior for deauthentication frames.
