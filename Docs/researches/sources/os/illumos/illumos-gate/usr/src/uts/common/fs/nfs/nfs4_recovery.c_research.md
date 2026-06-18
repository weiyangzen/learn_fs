# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_recovery.c

Purpose: Implements NFSv4 client recovery for server failover, stale client IDs, lost state, bad stateids/seqids, volatile filehandles, grace/delay handling, and reopen/relock flows.

Key behavior:
- `nfs4_needs_recovery` classifies transport, errno, and NFS status failures that require client recovery.
- `nfs4_start_recovery` converts errors into recovery actions, records lost state or bad-seqid requests, and starts or updates a per-mount recovery thread.
- `nfs4_start_fop` and `nfs4_end_fop` bracket normal NFSv4 operations with waits for grace/delay, delegation recall, filesystem recovery, recovery-error checks, server recovery locks, and volatile filehandle rename locks.
- The recovery thread drives a state machine: fail over to a responsive server, recover clientid, refresh security info, process bad seqids, reopen files, reclaim locks, resend lost state, and complete/notify waiters.
- Failover probes candidate servers with NULL RPCs, updates root/server filehandles, purges DNLC, marks files for remap, and moves mount state to the selected server.
- Clientid recovery calls `nfs4setclientid`, then triggers reopen recovery across all mounts sharing the server.
- Filehandle and stale-handle recovery remap files, distinguish per-file stale from filesystem-wide stale, and either fail over or mark affected rnodes dead.
- Open-file recovery builds a snapshot of valid open streams, optionally remaps files, reopens with `CLAIM_PREVIOUS` or `CLAIM_NULL`, and reclaims active locks.
- Lost state recovery resends OPEN, OPEN_DOWNGRADE, CLOSE, LOCK/LOCKU, and DELEGRETURN requests and performs compensating CLOSE after successful resent OPEN.
- Bad seqid recovery resets open-owner sequencing, marks lock owners bad, flags dangling lock owners on rnodes, and sends `SIGLOST`.

Dependencies:
- Uses NFSv4 client mount/server/rnode/open/lock/delegation structures, failover infrastructure, recovery locks, RPC client creation, DNLC, file locking, signals, zones, zthreads, callb CPR, DTrace, idmap headers, and event/fact logging.

Notable details:
- Recovery is serialized per mount with `MI4_RECOV_ACTIV` but can coordinate across all mounts sharing a server after clientid recovery.
- CLOSE, LOCKU, and DELEGRETURN are allowed limited retries even after rnode recovery errors so the client can release state.
- GRACE waits are tracked per mount; DELAY backoff is tracked per rnode with exponential growth.
- For lock reclaim failures, the owning process receives `SIGLOST`, and remaining locks for that pid are unregistered/skipped.
