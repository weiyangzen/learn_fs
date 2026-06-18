# sources/test-tools/pynfs/nfs4.0/servertests/st_setclientid.py

Purpose: Tests NFSv4.0 `SETCLIENTID` state-machine cases: valid initialization, client reboot invalidating old state, callback-info update, duplicate client ids across principals, lost replies, RFC case matrix, confirmed/unconfirmed replacement rules, many clients, and unconfirmed clientid use.

Important APIs/types/functions: Imports `os`, `struct`, `time`, `nfs_ops`, and `environment.check`. `_checkprinciples` is a stub that always returns true. Tests use `c.init_connection`, `c.setclientid`, `op.setclientid_confirm`, response fields `clientid` and `setclientid_confirm`, and owner ids built from pid/test names.

Control flow: Most tests call `init_connection` to create confirmed client records, send additional `SETCLIENTID` requests with same/different verifier bytes, and assert whether clientids/confirm verifiers are replaced or stale. Some tests create file state to make a client id active before duplicate-id checks.

State and persistence behavior: Heavily mutates server client records, confirmed and unconfirmed records, callback info, open state, and clientid-confirm verifiers.

Dependencies and integration points: Uses the pynfs client's SETCLIENTID/CONFIRM wrappers and response-array internals. Tests requiring different principals are limited by `_checkprinciples` being unimplemented.

Risks: Clientid replacement behavior is subtle and server-specific bugs are easy to expose. The principal-check stub weakens coverage for `CLID_INUSE` scenarios. `testLotsOfClients` creates 1024 client records and can be expensive.

Test signals: Checks success, `NFS4ERR_CLID_INUSE`, `NFS4ERR_EXPIRED`, and `NFS4ERR_STALE_CLIENTID`; direct failures validate zero confirm verifiers, reused clientids, reused confirms, and stale unconfirmed records.
