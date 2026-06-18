# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationResponse.py

Purpose: Tests reassociation response parsing and mutation, mirroring association response behavior for the reassociation subtype.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_REASSOCIATION_RESPONSE`, `Dot11ManagementReassociationResponse.get/set_capabilities`, `get/set_status_code`, `get/set_association_id`, supported-rates helpers, and vendor-specific helpers.

Control flow: Setup decodes a raw RadioTap sample and asserts class dispatch into the reassociation response object. Tests verify base-frame fields, raw body bytes, fixed response fields, rates, and vendor IEs.

State and persistence behavior: All state is transient packet-buffer mutation. Rate replacement shrinks the header and vendor IE append expands it.

Dependencies and integration points: Exercises subtype dispatch distinction between association response and reassociation response while sharing fixed body layout.

Risks: Because the layout matches association response, regressions may accidentally pass one subtype and fail the other if subtype mapping is wrong. Vendor IE appending must preserve pre-existing tuple content.

Test signals: Confirms reassociation response subtype mapping, AID/status/capability fields, sequence masking, rate humanization, and variable IE size accounting.
