# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_deleg_ops.c

Purpose: Provides FEM vnode monitors for files to which the NFSv4 server has granted delegations.

Key behavior:
- `recall_all_delegations` recalls outstanding delegations, optionally returns `NFS4ERR_DELAY` for nonblocking callers, and otherwise waits up to the lease time while retrying recalls.
- Read-delegation monitors recall on conflicting write/truncate/open/write/setattr/space/security operations.
- Write-delegation monitors permit server-owned operations but recall for non-owner opens, reads, writes, locks, setattr, space, and security changes.
- Vnode event monitors recall delegations for remove and rename source/destination events and always block until the delegation is returned.
- After conflict handling, each monitor forwards the operation to the next vnode operation with `vnext_*`.

Dependencies:
- Uses FEM, vnode/caller context APIs, NFSv4 server delegation state, `rfs4_recall_deleg`, `rfs4_dbe_*` entry synchronization, and the server caller ID.

Notable details:
- `CC_DONTBLOCK` callers receive `EAGAIN` through `CC_WOULDBLOCK`; remove and rename events deliberately ignore nonblocking behavior.
- The NFSv4 server’s own VOP calls are recognized through `cc_caller_id` to avoid self-conflict.
