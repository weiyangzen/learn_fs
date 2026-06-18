# File Research: sources/os/bsd/dragonflybsd/sys/sys/vnode.h

## Summary
Core vnode structure, vnode flags, I/O flags, vnode lifecycle APIs, and default VOP helper declarations.

## Main Responsibilities
- Defines `struct vnode`, including vnode lock/token/spinlock, I/O tracking, open/write counts, mount and ops vector, mount lists, buffer trees, type/tag, special unions, file size/object, namecache list, reference counts, poll info, resident image pointer, passthrough mount pointer, and last-write timestamp.
- Defines vnode flags, vnode state values, reference-count high bits, vmntvnodescan flags, and I/O flags.
- Defines permission mode bits and `VNOVAL`.
- Declares vnode allocation, lookup/open/read/write/stat/strategy/sync/reclaim/recycle/reference/lock APIs.
- Declares default VOP implementations and compatibility new-VOP helpers.

## Important Behavior
The comments describe the vnode as the center of file activity and document which fields require `v_token`, `v_spin`, or normal vnode locking. `v_ops` is double-indirect so a mount can swap active operation vectors dynamically, e.g. for journaling.

## Risks
This is one of the highest-risk shared kernel structures in the group. Reference counts encode termination/finalization bits, several fields have distinct locking rules, and buffer-tree/namecache/poll fields must be accessed with the correct token or spinlock.
