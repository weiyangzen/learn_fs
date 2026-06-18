# sources/test-tools/pynfs/nfs4.1/server41tests/st_compound.py

## Purpose
`st_compound.py` tests basic NFSv4.1 COMPOUND request validation: empty compounds, tags, invalid minor versions, and illegal or undefined opcodes.

## Important APIs, Types, and Functions
- `_simple_ops` builds a valid `EXCHANGE_ID` operation sequence.
- `testZeroOps`, `testGoodTag`, `testBadTags`, `testInvalidMinor`, `testInvalidMinor2`, and `testUndefined` each target one COMPOUND rule.
- `CustomPacker` inside `testUndefined` intentionally packs invalid opcodes.

## Control Flow
Tests send COMPOUND calls through `env.c1`, sometimes with custom tags or minor versions. Invalid opcode testing uses a packer override to force raw opnum emission when generated XDR packing would reject the object.

## State and Persistence Behavior
The tests mostly avoid persistent server state, except for `_simple_ops` creating or referencing client owner identity through `EXCHANGE_ID`.

## Dependencies and Integration Points
The module depends on `nfs_ops`, environment assertions, generated XDR types/constants, `rpc.rpc.RPCAcceptError`, and `nfs4lib.FancyNFS4Packer`.

## Risks and Edge Cases
The invalid UTF-8 test depends on server UTF-8 validation, which the local test server stubs out. The undefined-opcode behavior allows either `NFS4ERR_OP_ILLEGAL` or RPC `GARBAGE_ARGS` for some cases, reflecting protocol ambiguity noted in comments.

## Test Signals
Expected statuses include `NFS4_OK`, `NFS4ERR_INVAL`, `NFS4ERR_MINOR_VERS_MISMATCH` with empty result arrays, `NFS4ERR_OP_ILLEGAL`, and acceptable RPC-level `GARBAGE_ARGS`.
