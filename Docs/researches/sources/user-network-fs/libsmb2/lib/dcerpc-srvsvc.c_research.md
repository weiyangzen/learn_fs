# sources/user-network-fs/libsmb2/lib/dcerpc-srvsvc.c

Purpose: Implements NDR coders for the SRVSVC RPC interface, mainly share enumeration and share information retrieval.

Important APIs/functions: Exports `srvsvc_interface` and coders for share info levels 0, 1, and 2; share info containers; share enum/get-info unions and structs; `srvsvc_NetrShareEnum_req_coder`, `srvsvc_NetrShareEnum_rep_coder`, `srvsvc_NetrShareGetInfo_req_coder`, and `srvsvc_NetrShareGetInfo_rep_coder`.

Control flow: Request coders serialize server/share names as unique/ref UTF-16 pointers, serialize info levels and preferred maximum length/resume handle. Response coders decode switch-discriminated unions using request state where needed, allocate arrays for decoded share entries, decode nested strings and status codes.

State/persistence: No global mutable state except the interface descriptor. Decoded share structures and strings are payload-owned via `smb2_alloc_data` and are freed with the DCE/RPC payload.

Dependencies/integration: Depends on `libsmb2-dcerpc-srvsvc.h` type definitions and the core `dcerpc_*`/`ndr_*` coders. Examples `smb2-share-enum.c`, `smb2-share-enum-sync.c`, and `smb2-share-info.c` use these coders.

Risks: Only levels 0, 1, and 2 are implemented despite comments listing more IDL levels. Wire-provided `EntriesRead` directly controls allocation size and array loop counts. Some request/response coupling relies on `dcerpc_set_request`/`dcerpc_get_request` so decoding share get-info responses requires the original request pointer to remain valid.

Test signals: Existing `smb2-dcerpc-coder-test.c` covers UTF-16 and SHARE_INFO_1 containers for NDR32/NDR64. Add level 0/2, `NetrShareGetInfo`, unsupported-level behavior, large `EntriesRead`, and example-driven integration tests against a server.
