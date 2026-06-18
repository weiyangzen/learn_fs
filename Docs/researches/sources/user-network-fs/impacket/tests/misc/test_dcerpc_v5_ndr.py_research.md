# sources/user-network-fs/impacket/tests/misc/test_dcerpc_v5_ndr.py

Purpose: Regression-tests DCE/RPC NDR and NDR64 serialization for arrays, strings, padding, and null pointers.

Important APIs, types, and functions: Uses `NDRSTRUCT`, `NDRLONG`, `NDRSHORT`, `NDRUniFixedArray`, `NDRUniVaryingArray`, `NDRUniConformantVaryingArray`, `NDRVaryingString`, `NDRConformantVaryingString`, and `NDRPOINTERNULL`. Shared `NDRTest` supplies `create`, `do_test`, and round-trip validation.

Control flow: Each test class defines an inline NDR structure, populates it, serializes with and without `isNDR64`, checks hex output, reparses, and verifies reserialization stability.

State and persistence behavior: Pure in-memory serialization tests.

Dependencies and integration points: Protects low-level NDR packing used by all DCE/RPC v5 interfaces in Impacket.

Risks: NDR64 offset/count widths differ from classic NDR, making alignment regressions likely. Some conformant array coverage is commented out.

Test signals: Strong byte-level signal for fixed arrays, struct padding, varying/conformant strings and arrays, and null pointer representation.
