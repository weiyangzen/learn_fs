# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lease.c

Read completely. This file implements SMB2 lease support and lease-break handling, integrated with the existing oplock subsystem.

Lease lifecycle support includes `smb2_lease_init()`, `smb2_lease_fini()`, internal hold/release logic, lease hash computation, and `smb2_lease_create()`. Leases are stored in a server hash table keyed by lease key and client UUID. A lease is associated with one node, can be shared by multiple ofiles, and carries state, epoch, version, client UUID, and the ofile currently owning the underlying oplock.

`smb2_lease_break_ack()` decodes SMB2 lease break acknowledgements, looks up the lease, finds the ofile holding the lease oplock, validates the acknowledged state, clears breaking flags, calls `smb_oplock_ack_break()`, updates lease/ofile state, and persists durable state when needed.

Lease-break sending is handled by `smb2_lease_send_break()`. It builds an SMB2 lease-break notification, tries to send it on an active session associated with the lease, closes non-durable/nonpersistent handles when no connection is available, waits for ACKs when required, and performs local ACK downgrade on timeout or send failure.

`smb2_lease_acquire()` converts requested SMB2 lease caching bits into internal granular oplock state, respects tree oplock policy, attempts promotion in stages from write to handle to read caching, updates lease epoch and state on new grants, and may go async while waiting for oplock breaks.

`smb2_lease_ofile_close()` handles lease ownership transfer when the ofile owning the underlying oplock closes. It attempts to move the oplock to another open or durable/orphaned handle on the same lease, otherwise clears lease state and wakes ACK waiters.
