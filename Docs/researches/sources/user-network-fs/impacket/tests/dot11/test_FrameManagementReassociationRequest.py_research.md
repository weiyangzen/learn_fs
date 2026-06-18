# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationRequest.py

Purpose: Validates reassociation request parsing, including the current-AP address field and RSN/tagged parameters.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_REASSOCIATION_REQUEST`, `Dot11ManagementReassociationRequest.get/set_capabilities`, `get/set_listen_interval`, `get/set_current_ap`, SSID/rate/RSN helpers, and vendor-specific helpers.

Control flow: Setup decodes a RadioTap sample through management base to the reassociation request object. Tests mutate base fields, then body fixed fields and variable IEs.

State and persistence behavior: Packet object mutations are in-memory. Current AP and RSN setters rewrite body bytes, while variable IE changes update header-size metadata.

Dependencies and integration points: Extends association-request behavior with the current AP field, sharing the same management IE parser.

Risks: The current AP field sits between fixed fields and tagged parameters, so an incorrect fixed header length would break all subsequent IE parsing. Test names include a minor "Ressociation" typo but discovery remains unaffected.

Test signals: Covers subtype dispatch, fixed reassociation fields, SSID/rate/RSN replacement, vendor IE append ordering, and dynamic size changes.
