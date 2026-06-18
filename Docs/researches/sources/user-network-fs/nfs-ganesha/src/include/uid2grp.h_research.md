# sources/user-network-fs/nfs-ganesha/src/include/uid2grp.h

## Purpose
This header defines the UID/principal-to-group cache contract used by Ganesha's idmapper and credential-building paths.

## Important APIs, Types, And Control Flow
`group_data_t` stores uid, username buffer, primary gid, epoch, supplementary group count, refcount, mutex, and group array. It declares global `uid2grp_user_lock` and `uid2grp_sem`, cache init/add/lookup/remove/reap/clear functions, lookup helpers `uid2grp`, `uname2grp`, and `principal2grp`, plus reference-management APIs `uid2grp_unref`, `uid2grp_hold_group_data`, `uid2grp_release_group_data`, and expiration checks.

## State And Persistence
The cache is process-global in-memory state protected by a rwlock, per-record mutexes, refcounts, and a semaphore. Entries expire by epoch; no persistent storage is declared.

## Dependencies And Integration Points
It depends on pthreads, semaphores, `gsh_types.h`, and identity lookup wrappers. It integrates NFS principal/user resolution with request credential construction and access checks.

## Risks And Test Signals
Risks include stale group membership, refcount leaks, lock contention, semaphore misuse, and principal-to-uid ambiguity. Tests should cover cache hits/misses, expiration removal by uid/name, concurrent readers and reaper, large supplementary groups, principal fallback inputs, and unref/free races.
