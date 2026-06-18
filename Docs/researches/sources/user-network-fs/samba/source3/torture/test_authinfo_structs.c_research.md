# sources/user-network-fs/samba/source3/torture/test_authinfo_structs.c

## Purpose
`test_authinfo_structs.c` validates conversion between LSA trust-domain auth-info structures and Samba trust auth blobs. It is a local, non-network serialization round-trip test.

## Important APIs, types, and functions
`run_local_conv_auth_info()` is the exported test. `cmp_TrustDomainInfoBuffer` and `cmp_auth_info` compare nested auth-info buffers. `covert_and_compare` calls `auth_info_2_auth_blob` and `auth_blob_2_auth_info` and compares the result.

## Control flow
The test builds several combinations of incoming/outgoing current and previous auth arrays, including clear-text password entries and `TRUST_AUTH_TYPE_VERSION` entries. After each setup, it converts to incoming/outgoing blobs, converts back to `lsa_TrustDomainInfoAuthInfo`, and requires exact structural equality.

## State and persistence behavior
All data is stack or temporary talloc memory. It writes no remote or local durable state.

## Dependencies and integration points
It depends on generated LSA NDR types and `libcli/lsarpc/util_lsarpc.h` conversion helpers. It is registered as a local torture test through `proto.h`.

## Risks and test signals
The comparisons check counts, timestamps, auth types, sizes, data bytes, and null-vs-non-null previous arrays. Failures indicate trust password blob serialization regressions that could break trusted-domain persistence or interop.
