# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9auth.c

Implements Fossil's 9P authentication helpers around Plan 9 factotum RPC.

Key behavior:
- `authRead()` drives `auth_rpc(..., "read", ...)`, copies challenge data to clients, and on `ARdone` extracts `AuthInfo`, records `cuname`, and maps it to a uid.
- `authWrite()` feeds client auth data into the auth RPC.
- `authCheck()` validates attach authentication, including `NOFID` attach policy, auth fid matching, completion of auth protocol, uid mapping, and connection `aok` state.

Important implementation details:
- Console connections can attach without normal auth.
- `ConNoneAllow` and already-authenticated connections allow attaching as `none`.
- Auth fid must be `QTAUTH`, have matching `uname`, and target the same `Fsys`.
- Once an auth fid completes, the attach fid's `uname` is replaced with the authenticated `cuname`.

Risks and invariants:
- `authCheck()` uses `afid->alock` rather than a fid write lock because protocol progress can be required.
- Unknown users cause attach failure even after successful cryptographic authentication.
