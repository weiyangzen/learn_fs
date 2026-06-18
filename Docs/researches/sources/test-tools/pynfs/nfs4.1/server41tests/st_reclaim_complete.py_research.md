# sources/test-tools/pynfs/nfs4.1/server41tests/st_reclaim_complete.py

Purpose: tests `RECLAIM_COMPLETE` legality, no-grace behavior after completion, blocking of non-reclaim opens before completion, and duplicate completion errors.

Important APIs/types/functions: `testSupported`, `testReclaimAfterRECC`, `testOpenBeforeRECC`, and `testDoubleRECC`.

Control flow: tests create a fresh client/session, send `RECLAIM_COMPLETE` with root or current state, create/open files as needed, then attempt `CLAIM_PREVIOUS`, normal `OPEN`, or a second reclaim-complete and validate the expected NFS status.

State and persistence behavior: exercises per-client reclaim-complete state and grace-period enforcement. `testReclaimAfterRECC` creates confirmed open state only to attempt an invalid later reclaim and then closes it.

Dependencies/integration: uses the standard session/file helpers, `NFS4ops`, `nfs4lib`, and RFC 5661 status constants.

Risks and test signals: `testReclaimAfterRECC` passes a warnlist that appears to bitwise-OR two error constants instead of listing both separately, which may weaken warning handling. Grace-period behavior depends on server state at session creation.
