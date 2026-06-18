# sources/test-tools/pynfs/nfs4.0/servertests/st_openconfirm.py

Purpose: Tests NFSv4 `OPEN_CONFIRM` behavior for successful create-confirm flow, duplicate confirmation, missing filehandle, bad seqid, bad stateid, and stale stateid.

Important APIs/types/functions: Imports `stateid4`, `makeStaleId`, `nfs_ops.NFS4ops`, and `environment.check`. `_confirm` builds `use_obj(file) + [open_confirm]` using the current owner seqid. Public tests are `testConfirmCreate`, `testNoFh`, `testBadSeqid`, `testBadStateid`, and `testStaleStateid`.

Control flow: Tests create an unconfirmed open with `create_file`, extract the returned filehandle/stateid/rflags, and send explicit `OPEN_CONFIRM` operations. Error cases alter the filehandle, seqid, or stateid before confirmation.

State and persistence behavior: Mutates open-owner seqids and open state. A duplicate confirmation should fail because the state is already confirmed.

Dependencies and integration points: Relies on client wrapper internals such as `c.get_seqid(t.word())`, response-array indexes for OPEN results, and NFSv4 servers that may or may not set `OPEN4_RESULT_CONFIRM`.

Risks: Servers not requiring confirmation produce warning paths. Sequence-id expectations are tied to pynfs client-owner tracking.

Test signals: Checks `NFS4ERR_BAD_STATEID` for duplicate/bad stateid, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, and `NFS4ERR_STALE_STATEID`, with success for valid confirmation.
