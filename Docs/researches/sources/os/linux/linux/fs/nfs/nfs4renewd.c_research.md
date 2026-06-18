# File Research: sources/os/linux/linux/fs/nfs/nfs4renewd.c

This file implements the NFSv4 lease renewal worker. It runs as delayed work in kernel workqueue context rather than as a dedicated kernel thread.

Main functions:
- `nfs4_renew_state()` checks whether renewal should stop, determines whether the client is close enough to lease timeout or has delegations requiring callback renewal pressure, obtains renewal credentials through minor-version ops, schedules async renewal, expires delegations when only delegation renewal lacks credentials, marks lease expired when timeout renewal lacks credentials, reschedules renewal work, and expires unreferenced delegations.
- `nfs4_schedule_state_renewal()` schedules the next renewal for roughly two-thirds of the lease period after the last renewal, with a minimum delay of five seconds, and sets `NFS_CS_RENEWD`.
- `nfs4_kill_renewd()` synchronously cancels delayed renewal work.
- `nfs4_set_lease_period()` caps lease period at one hour, stores it in jiffies under client lock, and caps RPC reconnect timeout to at most half the lease.

Dependencies:
- Minor-version `state_renewal_ops` for credential selection and scheduling renewal RPCs.
- Delegation helpers for detecting, expiring, and pruning delegations.
- Client lock protects lease time updates and renewal scheduling calculations.

Risk areas:
- Renewal timing determines whether client open/lock/delegation state survives server lease expiration.
- Credential absence has different consequences for lease timeout renewal versus delegation-only renewal.
- `NFS_CS_STOP_RENEW` must be honored during shutdown to avoid renewing after teardown starts.
