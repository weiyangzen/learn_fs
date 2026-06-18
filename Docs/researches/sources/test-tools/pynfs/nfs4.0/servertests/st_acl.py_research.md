# sources/test-tools/pynfs/nfs4.0/servertests/st_acl.py

## Purpose
`st_acl.py` tests whether a server advertises, accepts, stores, and returns the `FATTR4_ACL` attribute. It covers support discovery, a simple ACL, and a larger ACL payload.

## Important APIs, Types, And Functions
- `testACLsupport(t, env)` calls `supportedAttrs` on the configured file and fails support if `FATTR4_ACL` is not advertised.
- `testACL(t, env)` creates a confirmed file, sets a one-entry ACL using `SETATTR`, then fetches `FATTR4_ACL`.
- `testLargeACL(t, env)` sets a twenty-entry ACL intended to produce a larger reply.
- The tests use `nfsace4` entries and `list2bitmap` for support masks.

## Control Flow
Tests initialize the connection, create a file where needed, build `PUTFH` plus `SETATTR` or `GETATTR` compounds, and assert OK with `check`. The support test gates later ACL cases through dependency metadata.

## State And Persistence Behavior
The module creates temporary files in the server export and mutates their ACL attributes. State persistence is only whatever the server stores between SETATTR and GETATTR in the same test.

## Dependencies And Integration Points
It imports NFSv4 constants/types, `check`, and `nfs4lib.list2bitmap`. It relies on `NFS4Client.create_confirm`, `setattr`, `getattr`, and the server's ACL implementation, which in the local Python server maps ACLs through `nfs4acl`.

## Risks And Edge Cases
- Comments note owner names are simple byte/integer strings and may not work under Kerberos name expectations.
- `testACL` checks successful GETATTR but does not compare the returned ACL to the set value.
- Large ACL behavior may expose max response or XDR packing issues, but the test currently only checks operation success.

## Test Signals
Signals are support-mask presence for `FATTR4_ACL`, successful `SETATTR(FATTR4_ACL)`, and successful `GETATTR(FATTR4_ACL)` after simple and larger ACL writes.
