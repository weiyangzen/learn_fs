# File Research: sources/os/linux/linux-stable/fs/lockd/svcshare.c

## Summary
DOS-style NLM share reservation management for lockd files.

## Main APIs
- `nlmsvc_share_file()` creates or updates a share reservation.
- `nlmsvc_unshare_file()` removes a matching reservation.
- `nlmsvc_traverse_shares()` purges shares matching a host predicate.

## Behavior
Shares are stored as a singly linked list on `nlm_file`. A reservation is keyed by host plus owner handle. New shares conflict if requested access intersects an existing share’s deny mode, or requested deny mode intersects an existing share’s access. Existing matching reservations are updated in place. Unshare returns success even when no matching share exists, per X/Open behavior.

## State and Dependencies
Each `struct nlm_share` embeds copied owner-handle bytes immediately after the allocation. The file-level share list is cleaned from `svcsubs.c` resource traversal. Operations first reject files that cannot be locked.

## Risks
The conflict expression is compact and asymmetric by naming: `access & existing mode` or `mode & existing access`. Share list lifetime depends on higher-level lockd serialization/resource traversal; this file itself has no lock.
