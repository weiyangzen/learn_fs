# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4renewd.c

This file implements the NFSv4 lease renewal worker. It is not a kernel thread; it runs as delayed work in kernel workqueue context.

Main functions:
- `nfs4_renew_state()`
  - Checks whether renewal should stop.
  - Computes whether the client is close enough to lease timeout.
  - Adds delegation callback renewal pressure when delegations are present.
  - Obtains state renewal credentials through minor-version ops.
  - Schedules async renewal via `sched_state_renewal()`.
  - Expires all delegations if only delegation renewal is needed but no credentials exist.
  - Marks lease expired when timeout renewal has no credentials.
  - Reschedules renewal work and expires unreferenced delegations.
- `nfs4_schedule_state_renewal()`
  - Schedules the next renewal at roughly two-thirds of the lease period after last renewal, with a minimum delay of 5 seconds.
  - Sets `NFS_CS_RENEWD`.
- `nfs4_kill_renewd()`
  - Cancels delayed renewal work synchronously.
- `nfs4_set_lease_period()`
  - Caps lease period at one hour.
  - Stores lease in jiffies.
  - Sets RPC reconnect timeout to at most half the lease.

Dependencies:
- Minor-version `state_renewal_ops`.
- Delegation helpers for detecting, expiring, and pruning delegations.
- Client lock protects lease time update and scheduling calculations.

Risk areas:
- Renewal timing determines whether client state survives server lease expiration.
- Credential absence is handled differently depending on whether renewal is needed for lease timeout or only delegations.
- `NFS_CS_STOP_RENEW` must be honored to avoid renewing during shutdown.
