# sources/user-network-fs/libsmb2/lib/dcerpc.c

Purpose: Implements libsmb2's DCE/RPC-over-SMB named-pipe transport and generic NDR/YAML coding layer used by SRVSVC and LSA clients.

Important APIs/functions: Context/PDU lifecycle: `dcerpc_create_context`, `dcerpc_connect_context_async`, `dcerpc_destroy_context`, `dcerpc_allocate_pdu`, `dcerpc_free_pdu`, `dcerpc_open_async`, `dcerpc_call_async`, `dcerpc_free_data`. NDR primitives include integer coders, `ndr_uint3264_coder`, pointer coders, array/union/struct coders, UTF-16 coders, UUID/context-handle coders, and test hooks `ndr_set_tctx`/`ndr_set_endian`. YAML encode-only helpers provide diagnostic rendering.

Control flow: A connect opens a named pipe with SMB2 create, sends a bind PDU proposing NDR32/NDR64 syntax, parses bind ACK, and selects context id. Calls allocate an NDR request PDU, encode header/request/stub, patch fragment length and allocation hint, send `SMB2_FSCTL_PIPE_TRANSCEIVE`, unfragment multi-fragment responses, decode response header/stub, and return payload-owned decoded data to the callback.

State/persistence: `struct dcerpc_context` stores the SMB context, pipe path, selected syntax, file id, transfer context id, data representation, and monotonically increasing call id. Each PDU tracks direction, encoding, payload memory context, deferred pointers, conformance pass state, request pointer, and YAML indentation state.

Dependencies/integration: Depends on SMB2 raw create/ioctl APIs, endian helpers, UTF-8/UTF-16 helpers, allocation context APIs, and public DCE/RPC headers. Service-specific files plug in request/response coders. Examples use it for SRVSVC and LSA workflows.

Risks: Deferred pointer list has fixed capacity `MAX_DEFERRED_PTR` but `dcerpc_add_deferred_pointer` does not bounds-check. Some decode counts are trusted by service coders. `dcerpc_uint64_coder` encodes `*(uint32_t *)ptr`, likely truncating 64-bit values on encode. `dce_unfragment_ioctl` rewrites response buffers in place and depends on consistent fragment lengths. YAML output uses `strncat`/`snprintf` against the output buffer and is encode-only. Error paths sometimes return `-ENOMEM` for generic encode failure.

Test signals: `tests/smb2-dcerpc-coder-test.c` covers NDR32 LE/BE and NDR64 LE for UTF-16 and share containers. Add tests for pointer overflow, NDR64 64-bit values, fragmented responses, bind rejection cases, YAML rendering, and service examples against real SMB named pipes.
