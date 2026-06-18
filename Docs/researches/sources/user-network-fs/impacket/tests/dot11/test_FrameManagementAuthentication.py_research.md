# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAuthentication.py

Purpose: Validates authentication management-frame decoding, fixed authentication fields, and vendor-specific tagged-parameter handling.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_AUTHENTICATION`, `Dot11ManagementAuthentication.get/set_authentication_algorithm`, `get/set_authentication_sequence`, `get/set_authentication_status`, and base management-frame duration/address/sequence helpers.

Control flow: `setUp` decodes a raw RadioTap capture and asserts the child chain reaches `Dot11ManagementAuthentication`. Tests cover base-frame fields, raw frame body, authentication triplet fields, and vendor-specific append behavior.

State and persistence behavior: No durable state. Setters rewrite in-memory packet data, and header-size checks verify appended vendor IEs are reflected in packet metadata.

Dependencies and integration points: Exercises `RadioTapDecoder` subtype dispatch and the common management-frame body parser used by many 802.11 management subclasses.

Risks: Authentication algorithm, sequence, and status are adjacent 16-bit fields; endian or offset regressions would produce plausible but wrong values. Vendor IE resizing remains a shared risk with other management tests.

Test signals: Good coverage for authentication subtype classification, class hierarchy, fixed field mutation, and vendor IE parsing/append.
