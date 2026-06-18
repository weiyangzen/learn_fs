# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationResponse.py

Purpose: Tests 802.11 association response decoding and mutation through Impacket's Dot11 management-frame hierarchy.

Important APIs, types, and functions: `TestDot11ManagementAssociationResponseFrames` uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_ASSOCIATION_RESPONSE`, `Dot11ManagementAssociationResponse.get/set_capabilities`, `get/set_status_code`, `get/set_association_id`, supported-rates accessors, and vendor-specific IE helpers.

Control flow: The setup phase decodes the raw RadioTap capture, checks class dispatch, extracts the management base, and then tests base-frame fields and association response body fields.

State and persistence behavior: Tests mutate packet objects in memory only. Supported-rate and vendor IE edits resize the body and provide direct signals that serialized packet layout remains coherent.

Dependencies and integration points: Depends on `six.PY2` for legacy assertion formatting and the Dot11 tagged-parameter parser for variable response body content.

Risks: Association ID and status fields are compact fixed-width values; endian or offset mistakes can silently corrupt later tagged parameters. Vendor IE appending must preserve pre-existing IE tuples.

Test signals: Confirms subtype dispatch, duration/address/sequence helpers, body bytes, response status/capability/AID fields, rate conversion, and vendor IE growth.
