# File Research: sources/os/linux/linux/fs/xfs/scrub/orphanage.h

## Role
Declares orphanage and adoption interfaces for online repair.

## Repair-Enabled API
- `xrep_orphanage_create` creates/attaches `/lost+found`.
- `xrep_orphanage_try_create` tolerates absent, non-directory, or no-space orphanage failures so repair can continue without adoption.
- Lock helpers manage orphanage IOLOCK/ILOCK state.
- `xrep_orphanage_rele` drops orphanage references.

## Adoption State
- `struct xrep_adoption` tracks scrub context, chosen name, parent-pointer args, block reservations, and whether to bump the child link count.
- Adoption helpers allocate the transaction, compute a unique name, move the file, and roll the transaction.

## Non-Repair Build
When `CONFIG_XFS_ONLINE_REPAIR` is disabled, adoption is an empty structure and orphanage release is a no-op.
