# File Research: sources/os/linux/linux/fs/nfsd/nfs4state.c

## Summary
Implements the Linux NFSD NFSv4 state engine. It owns client IDs, sessions, replay slots, open/share state, byte-range lock state, delegations, copy-notify stateids, grace-period recovery, courtesy-client expiry, and per-client nfsdfs inspection/control files.

## Main Responsibilities
- Creates and tears down global and per-net NFSv4 state infrastructure, including slabs, the `nfs4_file` rhltable, session DRC-slot shrinker, per-net client/session tables, laundromat work, and state shrinkers.
- Handles NFSv4.0 client establishment with `SETCLIENTID` / `SETCLIENTID_CONFIRM` and NFSv4.1+ `EXCHANGE_ID`, `CREATE_SESSION`, `SEQUENCE`, `BIND_CONN_TO_SESSION`, `DESTROY_SESSION`, and `DESTROY_CLIENTID`.
- Maintains stateowner and stateid lifetimes for open, lock, delegation, layout-related open/deleg counters, and server-to-server copy notify state.
- Implements OPEN, OPEN_CONFIRM, OPEN_DOWNGRADE, CLOSE, DELEGRETURN, FREE_STATEID, TEST_STATEID, RENEW, LOCK, LOCKT, LOCKU, and RELEASE_LOCKOWNER state processing.
- Grants, recalls, revokes, and reaps delegations, including write/read delegation timestamp support and CB_GETATTR conflict handling.
- Drives grace-period and recovery behavior through reclaim records, `RECLAIM_COMPLETE`, lock grace integration, and the laundromat.

## Key Data Structures and State
- `nfs4_client` objects are indexed by confirmed/unconfirmed clientid hash tables and name red-black trees under `nfsd_net.client_lock`; they carry credentials, callbacks, sessions, stateid IDR, openowners, delegations, revoked state, async copy state, and nfsdfs dentries.
- `nfsd4_session` objects are indexed by sessionid hash tables, per-client lists, and the global session list; each owns an xarray of replay/cache slots whose target count can grow on demand and shrink under pressure.
- `nfs4_file` objects are keyed primarily by inode in an `rhltable`, with filehandle disambiguation for aliases; they aggregate share access/deny counters, cached `nfsd_file` opens, open/lock stateids, delegations, pNFS open/delegation state counters, and delegation lease files.
- `nfs4_stateowner` represents openowners and lockowners, including NFSv4.0 seqid replay state. Openowners also retain a last-closed stateid on `close_lru` for CLOSE replay.
- `nfs4_stid` / `nfs4_ol_stateid` instances are IDR-backed per-client stateids. Open stateids own share reservations, lock stateids link to parent opens, delegations own leases and callbacks, and status bits encode closed, revoked, admin-revoked, freeable, and freed states.
- Blocked locks use `nfsd4_blocked_lock` with VFS lock-manager callbacks, per-lockowner lists, a per-net LRU, and CB_NOTIFY_LOCK callbacks.

## Important Behavior
Client identity paths distinguish credential/verifier matches, reboot/update cases, confirmed versus unconfirmed records, MACH_CRED enforcement, and NFSv4.0 versus session-based clients. Expired clients are hidden by setting `cl_time` to zero and removing them from lookup structures before destruction.

Session `SEQUENCE` enforces slot seqids, request size and op-count limits, connection binding, replay-cache validation, dynamic slot growth, and response buffer limits. Reply caching stores only the data after the initial SEQUENCE response and never updates the cache for a failing solo SEQUENCE.

OPEN processing is split between `nfsd4_process_open1()` allocation/owner/seqid setup and `nfsd4_process_open2()` file insertion, share conflict checks, VFS file acquisition, truncation, stateid generation, and optional delegation grant. Courtesy-client conflicts can be resolved by expiring the conflicting courtesy client and scheduling the laundromat.

Delegation granting uses kernel leases and rejects unsafe cases such as recent conflicts, alias ambiguity with writers, unsupported export lock recovery, setuid/setgid write opens, duplicate per-client delegations, and dentry races after lookup. Recalls use CB_RECALL, a short-lived bloom filter to avoid immediately regranting recalled filehandles, and LRU revocation after lease expiry.

Lock operations translate NFSv4 ranges and lock types to VFS POSIX locks, handle reclaim versus grace-period rules, allocate or reuse lock stateids, maintain lockowner seqids, support async blocking locks with callback notification, and report conflict owner/client details when available.

The laundromat ends grace when safe, expires COPY_NOTIFY state, reaps async copies, transitions idle active clients to courtesy clients, expires courtesy/expirable clients, cleans NFSv4.0 admin-revoked state after a lease, revokes timed-out delegations, frees old CLOSE replay state, drops stale blocked locks, services inter-SSC delayed unmounts, and triggers delegation recall-any under pressure.

The nfsdfs client interface exposes `info`, `states`, and `ctl`; `ctl` accepts `expire\n` and waits for in-flight RPC users and destruction to finish. The state listing formats open, lock, delegation, and layout stateids with file, owner, access, deny, and admin-revoked information.

## Dependencies
Uses NFSD VFS/filecache helpers, SunRPC/GSS credential machinery, NFSv4 XDR/callback code, VFS locks and leases, export operations, fsnotify for client dentry changes, rhashtable/rhltable, xarray, IDR, shrinkers, delayed workqueues, per-net NFSD state, pNFS hooks, and optional NFSv4.2 inter-server copy support.

## Risks and Subtleties
The file is concurrency-heavy: `client_lock`, per-client `cl_lock`, per-file `fi_lock`, `deleg_lock`, blocked-lock locks, stateid mutexes, lease locks, IDR references, callback references, wait queues, and workqueues interact. Many cleanup paths deliberately unhash state first, then drop persistent references later to avoid races with CLOSE replay, callbacks, and in-flight RPCs.

Security-sensitive checks are spread across client credential matching, MACH_CRED validation, export permission checks after reusing stateid files, owner override for stateid I/O, and delegation/open conflict decisions. Bypassing the preprocess helpers can miss stale clientid, revoked stateid, current-stateid, filehandle, generation, or openmode validation.

Protocol edge cases are encoded directly: special zero/one/current/close stateids, NFSv4.0 seqid replay, v4.1 ignored zero generations, v4.0 admin-revoked state retention, reclaim-complete tracking, lease/grace interactions, close replay state, OPEN_XOR_DELEGATION, delegated timestamps, CB_GETATTR fallback to recall, and server-to-server COPY_NOTIFY stateids.
