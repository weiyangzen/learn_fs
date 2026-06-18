# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc.h

## Purpose
`libsmb2-dcerpc.h` defines the generic DCERPC/NDR API layered on top of libsmb2.

## Important APIs, Types, and Functions
It defines data-representation constants, `dcerpc_coder`, `enum dcerpc_encoding`, pointer kinds, UUID/syntax/context-handle types, `struct dcerpc_utf16`, global interface IDs for LSA and SRVSVC, callback type `dcerpc_cb`, context lifecycle functions, async connect/open/call functions, PDU allocation/free helpers, request/size/switch metadata accessors, and NDR/DCERPC scalar/string/array/union/struct coder helpers.

## Control Flow
A caller creates a DCERPC context from an SMB2 context, connects to a named pipe with an interface syntax, opens/binds, then issues `dcerpc_call_async()` with request and reply coders. Coders advance an iovec offset while encoding or decoding data according to NDR rules and pointer metadata.

## State and Persistence Behavior
`struct dcerpc_context` and `struct dcerpc_pdu` are opaque. They retain transport binding, encoding mode, request metadata, and allocated decoded data until freed. No on-disk persistence occurs.

## Dependencies and Integration Points
It integrates with SMB named-pipe I/O and higher-level LSA/SRVSVC headers. It uses `struct smb2_iovec` and `struct smb2_context` from the libsmb2 API surface.

## Risks and Edge Cases
NDR alignment, endianness, conformant/varying array sizes, and pointer referent handling are easy to break. Async callbacks must respect context lifetime and free decoded data with the correct context.

## Test Signals
Test bind/open/call flows for LSA and SRVSVC, little and big endian NDR if supported, null/unique/full pointer handling, UTF-16 strings, arrays, unions, decode failures, and callback lifetime.
