# File Research: sources/os/linux/linux-stable/fs/nfsd/state.h

## Summary
Defines NFSD’s NFSv4 state model: clientids, stateids, sessions, callbacks, delegations, open/lock owners, pNFS layout state, copy state, reclaim records, and blocked locks.

## Contents
Core types include `clientid_t`, `stateid_t`, `nfs4_stid`, `nfs4_client`, `nfsd4_session`, `nfsd4_slot`, `nfs4_stateowner`, `nfs4_openowner`, `nfs4_lockowner`, `nfs4_file`, `nfs4_ol_stateid`, `nfs4_delegation`, `nfs4_layout_stateid`, `nfs4_cpntf_state`, and `nfsd4_blocked_lock`.

## Important Details
Stateid status/type bits distinguish open, lock, delegation, and layout state plus closed/revoked/freeable states. Clients carry id hashes, owner hashes, stateid IDRs, delegation lists, session lists, callback state, reclaim flags, courtesy/expirable state, async copy state, and nfsdfs debug dentries. Sessions have forward slot xarrays and backchannel slot bitmaps. Delegations embed callback and CB_GETATTR state.

## Main APIs
Declares stateid lookup/preprocessing, stateid allocation/freeing, callback scheduling, client reclaim tracking, copy-notify state management, delegation conflict checks, callback net init/shutdown, state revocation, copy cancellation, and grace-period forcing.

## Risks
This header encodes many lifetime and lock contracts used by `nfs4state.c` and related modules. Refcounts span clients, sessions, stateids, owners, files, callbacks, layouts, delegations, and blocked locks. Incorrect status-bit ownership or stale stateid generation comparisons can cause replay errors, state leaks, delegation failures, or use-after-free races.
