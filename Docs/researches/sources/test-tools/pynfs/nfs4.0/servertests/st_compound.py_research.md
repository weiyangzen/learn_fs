# sources/test-tools/pynfs/nfs4.0/servertests/st_compound.py

## Purpose
`st_compound.py` tests NFSv4 COMPOUND request-level behavior: zero operations, valid and invalid tags, minor-version rejection, undefined opcodes, malformed op packing, and long compounds.

## Important APIs, Types, And Functions
- `testZeroOps(t, env)` sends an empty compound and expects OK.
- `testGoodTag(t, env)` verifies a valid UTF-8 tag is echoed in the response.
- `testBadTags(t, env)` iterates invalid UTF-8 byte strings and expects `NFS4ERR_INVAL`.
- `testInvalidMinor(t, env)` sends minor version 50 and expects `NFS4ERR_MINOR_VERS_MISMATCH`.
- `testUndefined(t, env)` builds an undefined op (`argop=100`) and expects `NFS4ERR_OP_ILLEGAL`, then monkey-patches a packer to emit an invalid opcode and expects an RPC/XDR failure.
- `testLongCompound(t, env)` sends a repeated `PUTROOTFH` sequence and accepts OK or `NFS4ERR_RESOURCE`.

## Control Flow
The tests call `c.compound` with explicit tags/minor versions or raw operation lists. `testUndefined` uses `nfs_argop4` and a custom `NFS4Packer` subclass to produce a malformed operation that cannot be normally packed. It catches `RPCError` for the malformed case as the expected transport-level failure.

## State And Persistence Behavior
The tests do not create persistent state. They exercise COMPOUND parser/dispatcher behavior and current filehandle reset with repeated PUTROOTFH operations.

## Dependencies And Integration Points
Imports include NFS constants/types/packer, `check`, invalid UTF-8 generator, `RPCError`, and `nfs_ops`. It directly exercises server request unpacking and operation dispatch in `NFS4Server.O_Compound`.

## Risks And Edge Cases
- Malformed-op expectations may vary by RPC stack; the test expects an RPC-level exception rather than a normal NFS status.
- Long-compound length is hard-coded at 500 operations and accepts resource exhaustion as compliant.
- Invalid tag behavior depends on byte/string handling in the packer and server UTF-8 validation.

## Test Signals
Signals are COMPOUND response status and tag echo, minor-version mismatch, illegal op status for undefined operations, RPC failure on impossible packed opcode, and no crash/resource behavior for long operation arrays.
