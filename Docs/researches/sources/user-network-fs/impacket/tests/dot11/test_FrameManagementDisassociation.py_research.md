# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDisassociation.py

Purpose: Validates Dot11 disassociation frame decoding and reason-code accessors.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_DISASSOCIATION`, `RadioTapDecoder.decode`, `Dot11ManagementFrame` duration/address/sequence helpers, and `Dot11ManagementDisassociation.get_reason_code` / `set_reason_code`.

Control flow: The setup phase decodes a full RadioTap sample and checks class dispatch down to `Dot11ManagementDisassociation`; tests then mutate base fields and the body reason code.

State and persistence behavior: All packet state is transient and in memory. Setters update the backing packet buffer; no persistent outputs are produced.

Dependencies and integration points: Shares the common management-frame base with association, authentication, and deauthentication tests.

Risks: Like deauthentication, the body is only two bytes, so incorrect body offsets or FCS handling would dominate failures. Python 2/3 class-string assertions add legacy compatibility noise.

Test signals: Confirms subtype classification, address setters, sequence-number masking, frame-body extraction, and disassociation reason-code mutation.
