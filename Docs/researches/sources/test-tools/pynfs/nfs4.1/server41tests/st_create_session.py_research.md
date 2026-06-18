# sources/test-tools/pynfs/nfs4.1/server41tests/st_create_session.py

## Purpose
`st_create_session.py` tests NFSv4.1 `CREATE_SESSION` behavior, including basic creation, replay handling, principal changes, invalid clientids, callback security parameters, RDMA arrays, channel limits, response-size errors, and DRC memory stress.

## Important APIs, Types, and Functions
- `create_session(c, clientid, sequenceid, cred=None, flags=0)` sends a basic `CREATE_SESSION`.
- Tests include `testSupported1`, `testSupported2`, `testSupported2b`, `testNoExchange`, replay tests, bad sequence tests, principal collision tests, callback security/RDMA tests, channel limit tests, and stress tests like `testDRCMemLeak`.

## Control Flow
Most tests create a client through `env.c1.new_client`, then call either the client's high-level `create_session` or the module helper with custom args. Replay tests resend identical or sequence-wrapped requests and compare responses with tags cleared. Limit tests construct custom `channel_attrs4`.

## State and Persistence Behavior
The file exercises unconfirmed and confirmed client records, per-client `CREATE_SESSION` sequence ids, session replay cache, session tables, backchannel callback configuration, and DRC memory allocation under repeated failed calls.

## Dependencies and Integration Points
It depends on `nfs_ops`, environment helpers, generated channel/callback types, `nfs4lib`, threading, and RPC error classes. It integrates with callback handling through client program hooks and callback security parameter arrays.

## Risks and Edge Cases
Some tests use large iteration counts (`10000`) or rely on servers returning SHOULD-level errors like `NFS4ERR_TOOSMALL`. Callback program/version tests are Ganesha-flagged and depend on transient callback behavior. Some server implementations may accept or reject RDMA array encodings differently.

## Test Signals
Signals include `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_SEQ_MISORDERED`, `NFS4ERR_CLID_INUSE`, `NFS4ERR_INVAL`, `NFS4ERR_BADXDR` or `GARBAGE_ARGS`, `NFS4ERR_NOT_ONLY_OP`, `NFS4ERR_TOOSMALL`, `NFS4ERR_REP_TOO_BIG`, and `NFS4ERR_REP_TOO_BIG_TO_CACHE`.
