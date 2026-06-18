# sources/test-tools/pynfs/nfs4.0/servertests/st_gss.py

## Purpose
`st_gss.py` tests RPCSEC_GSS error handling around NFSv4 compounds. It deliberately corrupts GSS sequence numbers, header fields, verifier checksums, data checksums, procedure numbers, service numbers, and high sequence numbers, then verifies RPC-level denial or accept errors.

## Important APIs, Types, And Functions
- `BadGssHeader(sec, bad_cred_funct)` wraps an existing security object, overrides credential creation, passes through most attributes, and leaves secure/unsecure data as identity for cases expected to fail before body protection.
- `_using_gss`, `_using_service`, and `_using_integrity` are dependency predicates for the test runner.
- `testBadGssSeqnum` decrements the outgoing GSS sequence and expects a timeout or dropped reply.
- `testInconsistentGssSeqnum` changes the body credential sequence after the header and expects `GARBAGE_ARGS`.
- `testBadVerfChecksum` corrupts verifier checksum input and expects `RPCSEC_GSS_CREDPROBLEM`.
- `testBadDataChecksum` corrupts integrity-protected data and expects `GARBAGE_ARGS`.
- `testBadVersion`, `testHighSeqNum`, `testBadProcedure`, and `testBadService` mutate credential header fields and expect appropriate auth errors.

## Control Flow
Tests first ensure a normal `PUTROOTFH` compound works where useful. They then monkey-patch methods or replace `c.security` with `BadGssHeader`, issue a simple compound, catch expected `timeout`, `OSError`, `RPCAcceptError`, or `RPCDeniedError`, and restore the original security object in `finally` blocks.

## State And Persistence Behavior
The module mutates only the client-side security object and sequence counters during a test and restores them afterward. Server state is not intentionally changed beyond simple `PUTROOTFH` compounds and RPC context behavior.

## Dependencies And Integration Points
Imports include NFS constants, `check`, socket timeout, `rpc.rpc`, `rpc.rpcsec.gss_const`, `rpc_gss_cred_t`, and `nfs_ops`. The tests depend on RPCSEC_GSS support in `rpc.supported`, the selected environment security flavor, and the security object's packer/checksum APIs.

## Risks And Edge Cases
- GSS tests are transport/security-stack dependent and may produce timeouts, OS errors, accept errors, or denied errors depending on implementation.
- Monkey-patching security methods must exactly match the expected method signatures; `testBadDataChecksum` assumes the integrity `secure_data` signature takes `(data, seqnum)`.
- Some failure messages contain typos but do not affect behavior.

## Test Signals
Signals are dropped replies for replayed/old GSS sequence numbers, `rpc.GARBAGE_ARGS` for inconsistent body/header or bad data checksum, `rpc.AUTH_ERROR` with `RPCSEC_GSS_CREDPROBLEM`, `RPCSEC_GSS_CTXPROBLEM`, or `AUTH_BADCRED` for malformed credentials.
