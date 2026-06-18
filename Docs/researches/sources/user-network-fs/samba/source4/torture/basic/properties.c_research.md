# sources/user-network-fs/samba/source4/torture/basic/properties.c

## Purpose
This file prints negotiated server capabilities and filesystem attributes. It is an inspection test rather than a deep mutating torture scenario.

## Important APIs, types, and functions
The core helpers are `struct bitmapping`, `BIT_NAME`, `show_bits()`, and exported `torture_test_properties()`. It uses `cli->transport->negotiate.capabilities` and `smb_raw_fsinfo()` with `RAW_QFS_ATTRIBUTE_INFO`.

## Control flow
`torture_test_properties()` prints the capability mask, decodes known capability bits, queries filesystem attribute information, decodes known filesystem flags, and prints max component length and filesystem type. Failure to query fsinfo sets `correct=false`.

## State and persistence
The test is read-only from the server perspective and has no local persistent state.

## Dependencies and integration points
It depends on negotiated SMB capability constants and filesystem attribute constants, plus the raw fsinfo API. It is useful as context for interpreting other torture failures because it reveals DFS, NT SMB, Unicode, large file, ACL, sparse file, named stream, and similar capability claims.

## Risks
Unknown bits are only printed, not failed. Some attributes are server-advertised capabilities, not proof that all related behavior is correct.

## Test signals
Primary signals are a failed `RAW_QFS_ATTRIBUTE_INFO` request, missing expected capability/attribute bits for a test environment, or unexpected unknown bit masks.
