# File Research: sources/os/linux/linux/fs/lockd/svcshare.c

## Purpose
`svcshare.c` manages NLM DOS-style share reservations on server-side `nlm_file` objects. These reservations are separate from POSIX byte-range locks and track host, owner handle, requested access, and deny mode.

## Main Responsibilities
- Compares share owner handles with `nlm_cmp_owner()`.
- Adds or updates a share reservation in `nlmsvc_share_file()`.
- Removes a matching reservation in `nlmsvc_unshare_file()`.
- Removes all shares matching a host predicate in `nlmsvc_traverse_shares()`.

## Control Flow
`nlmsvc_share_file()` first rejects files that cannot be locked. It scans existing shares on the file. A matching host/owner updates access and mode in place. A conflicting access/mode pair returns `nlm_lck_denied`. If no entry exists, it allocates one object plus trailing owner-handle storage, copies the owner handle, links it into `file->f_shares`, and returns granted.

`nlmsvc_unshare_file()` scans the file's singly linked share list and deletes the matching host/owner entry. If no matching share exists, it still returns granted, matching the X/Open behavior noted in the comment.

## Integration Points
- Called by NLM v1/v3 and v4 SHARE/UNSHARE procedure handlers.
- Traversed by `svcsubs.c` when freeing host resources or invalidating all client resources.
- Uses `nlmsvc_file_cannot_lock()` as the same file usability gate as lock paths.

## Risks and Edge Cases
- The share list is a simple singly linked list under higher-level file traversal/operation serialization; this file does not take its own lock.
- Conflict detection is based on `(access & existing_mode) || (mode & existing_access)`.
- Allocation stores owner bytes inline after `struct nlm_share`, so object lifetime must match the list entry exactly.
