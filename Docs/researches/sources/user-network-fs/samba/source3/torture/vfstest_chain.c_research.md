<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest_chain.c -->
# sources/user-network-fs/samba/source3/torture/vfstest_chain.c

## Purpose
`vfstest_chain.c` adds a `cmd_test_chain()` command that regression-tests SMB1 chained request detection, chain length calculation, and parsing using embedded packet byte arrays, including malformed examples.

## Important APIs, types, and functions
- Static byte arrays such as `nonchain1_data`, `nonchain2_data`, `chain1_data`, `chain2_data`, `bug_8360_data`, `invalid1_data`, and `invalid2_data` are captured SMB1/NBSS request buffers.
- `cmd_test_chain()` calls `smb1_is_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` and accumulates boolean success.

## Control flow
The command first verifies that known single requests are not chains, then verifies chain status and exact chain lengths for known chained requests and a bug 8360 regression packet. It then checks invalid buffers return non-chain and expected lengths, and finally parses two valid chains into `struct smb_request **` arrays. It returns `NT_STATUS_OK` only if every predicate passes.

## State and persistence behavior
There is no persistent state. The only allocations are parser outputs under `talloc_tos()` during `smb1_parse_chain()`. The packet fixtures are static read-only data.

## Dependencies and integration points
This file depends on `vfstest.h` and smbd SMB1 parser helpers from `smbd/smbd.h`. It is conditionally compiled into `vfstest` by `wscript_build` only when `WITH_SMB1SERVER` is configured.

## Risks and edge cases
- The test relies on hard-coded binary packets; fixture corruption or endian-sensitive parser changes can make failures difficult to diagnose.
- It does not inspect parsed request contents, only parse success and count.
- `requests` is reused without explicit freeing inside the command, relying on the surrounding talloc stack behavior.

## Test signals
The command itself is a focused selftest: `NT_STATUS_OK` means chain detection, length calculation, invalid-buffer handling, and basic parsing still match the embedded fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest_chain.c -->
