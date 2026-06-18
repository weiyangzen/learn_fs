# sources/user-network-fs/libsmb2/examples/smb2-share-enum.c

Purpose: This asynchronous example enumerates SMB shares and also prints a YAML encoding of the SRVSVC response.

Important APIs and types: It uses `smb2_share_enum_async`, `srvsvc_NetrShareEnum_rep`, DCE/RPC YAML encoding with `dcerpc_allocate_pdu`, `dcerpc_do_coder`, `srvsvc_NetrShareEnum_rep_coder`, and the normal SMB2 poll loop.

Control flow: The program parses optional level, connects to `IPC$`, starts async share enumeration, services the SMB fd until callback completion, prints shares by level, creates a DCE/RPC context to encode the response as YAML, frees decoded data, then cleans up.

State and persistence behavior: Runtime state includes global `is_finished`, selected level, decoded response, and a static YAML buffer. There is no persistence.

Dependencies and integration points: It exercises async SRVSVC helpers, DCE/RPC generated coders, YAML encoding, and SMB event-loop integration.

Risks: The comment says it always uses Level1, but the code supports level 0 and 1 via global `level`. YAML buffer size is fixed at 65536. Error paths exit without full cleanup.

Test signals: Output should match synchronous share enumeration plus valid YAML for the decoded response. Large share lists test YAML buffer sufficiency.
