# sources/user-network-fs/libsmb2/lib/dcerpc-lsa.c

Purpose: Implements NDR coders for the LSA RPC interface used to open policy handles, resolve SIDs, and close handles over the shared DCE/RPC transport.

Important APIs/functions: Exports `lsa_interface`, `NT_SID_AUTHORITY`, and coders such as `lsa_RPC_SID_coder`, `lsa_RPC_UNICODE_STRING_coder`, `lsa_Close_req_coder`, `lsa_Close_rep_coder`, `lsa_OpenPolicy2_req_coder`, `lsa_OpenPolicy2_rep_coder`, `lsa_LookupSids2_req_coder`, and `lsa_LookupSids2_rep_coder`. Internal coders handle SID arrays, translated names, object attributes, trust/domain lists, and referenced domain lists.

Control flow: Request coders serialize handles, SID buffers, lookup parameters, and object attributes through core NDR primitives. Response coders allocate payload-owned arrays when decoding counts from the wire, then decode nested unique/reference pointers and status values. `OpenPolicy2` encodes an empty object-attributes structure; `LookupSids2` encodes lookup options and client revision constants.

State/persistence: No global mutable state beyond exported interface/SID authority data. Decoded allocations are attached to the DCE/RPC PDU payload memory context and must be released with `dcerpc_free_data`.

Dependencies/integration: Depends on public LSA type definitions in `libsmb2-dcerpc-lsa.h` and generic coders in `dcerpc.c`. Examples in `examples/smb2-lsa-lookupsids.c` exercise connect to `lsarpc`, open policy, lookup SIDs, and close.

Risks: Wire-provided counts drive allocations and loops with limited range enforcement in this file, despite comments showing IDL ranges. Some count variables are `uint64_t` but loop indices are `int`, so very large values can misbehave if not rejected by lower layers. Unicode string length computation uses `strlen * 2` and assumes UTF-8-to-UTF-16 handling in the generic coder.

Test signals: Extend `smb2-dcerpc-coder-test.c` with LSA SID/name/domain list round trips for NDR32/NDR64 and endian variants. Integration tests should run the LSA lookup example against a known SMB server and verify memory cleanup through `dcerpc_free_data`.
