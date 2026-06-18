# sources/user-network-fs/libsmb2/examples/smb2-share-info.c

Purpose: This asynchronous example fetches information about one SMB share through SRVSVC `NetrShareGetInfo` and prints both human-readable and YAML output.

Important APIs and types: It uses `dcerpc_connect_context_async`, `SRVSVC_NETRSHAREGETINFO`, `srvsvc_NetrShareGetInfo_req_coder`, `srvsvc_NetrShareGetInfo_rep_coder`, `srvsvc_NetrShareGetInfo_req`, `srvsvc_NetrShareGetInfo_rep`, share type constants, DCE/RPC YAML encoding, and the SMB2 poll loop.

Control flow: The program parses optional `-l level`, parses a URL whose share component is the target share, connects to `IPC$`, binds to `srvsvc`, allocates a request with `\\server` and share name, calls `NetrShareGetInfo`, prints the level-1 style summary, YAML-encodes the request and response, frees allocated request/server strings and decoded data, and marks completion.

State and persistence behavior: It reads server share metadata only. Runtime state includes global request pointer, server string, selected level, DCE context, and static YAML buffer.

Dependencies and integration points: It validates lower-level DCE/RPC usage for SRVSVC, request/response coders, and YAML encoding beyond the convenience `smb2_share_enum` APIs.

Risks: Default `level` is uninitialized unless `-l` is supplied, which can send an unintended request level. The callback creates a new DCE context using the SMB2 context and then calls `dcerpc_free_data(dce, rep)` after destroying that new context, which is a suspicious lifetime pattern. It prints fields as `ShareInfo1` regardless of selected level.

Test signals: Run with explicit `-l 1` and compare output/YAML to server share properties. Invalid or unsupported levels should be tested because the code does little validation.
