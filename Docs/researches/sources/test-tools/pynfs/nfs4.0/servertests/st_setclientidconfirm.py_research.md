# sources/test-tools/pynfs/nfs4.0/servertests/st_setclientidconfirm.py

Purpose: Tests `SETCLIENTID_CONFIRM` error and state-machine behavior for unknown clientids, a case not covered by the RFC, and selected RFC confirmation cases.

Important APIs/types/functions: Imports `os`, `nfs_ops.NFS4ops.setclientid_confirm`, and `environment.check`. Public tests are `testStale`, `testBadConfirm`, and `testAllCases`.

Control flow: `testStale` confirms clientid `0`. `testBadConfirm` initializes a client, sends another `SETCLIENTID`, then reconfirms the first pair. `testAllCases` sequences confirmations and new `init_connection` calls with different verifiers.

State and persistence behavior: Mutates confirmed and unconfirmed clientid records and confirm verifiers.

Dependencies and integration points: Tightly coupled to the pynfs client initialization helper and raw `SETCLIENTID_CONFIRM` op constructor.

Risks: Some behavior is explicitly marked ganesha or "case not covered in RFC"; portability may vary. The final RFC-case sequence is more of an execution path check than exhaustive validation.

Test signals: `NFS4ERR_STALE_CLIENTID` for unknown/stale confirmations and success for accepted confirmation transitions.
