<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c -->
# sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c

Purpose: Offline coder regression test for libsmb2 DCE/RPC NDR encoding and decoding.

Important APIs, types, and functions: Defines `test_dcerpc_coder`, comparison helpers for UTF-16 and SRVSVC share structures, concrete tests for NDR32 little/big endian and NDR64 little endian, and `main` creating SMB2/DCE contexts.

Control flow: Each test encodes a request structure to a fixed buffer, checks offset and byte-for-byte expected output, normalizes fake unique pointer markers, decodes into a fresh structure, and compares semantic fields.

State and persistence behavior: Uses stack fixtures and allocated decode buffers. DCE/RPC context is transient and no network calls are made.

Dependencies and integration points: Depends on libsmb2 DCE/RPC, LSA, SRVSVC headers and coder internals `ndr_set_tctx`/`ndr_set_endian`. Integrated by `test_900_dcerpc.sh`.

Risks: Large embedded byte arrays are brittle but valuable; any legitimate encoding change needs fixture updates. Coverage is focused on selected structures, not all DCE/RPC coders.

Test signals: Directly run by `test_900_dcerpc.sh` and gives strong byte-level regression signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c -->
