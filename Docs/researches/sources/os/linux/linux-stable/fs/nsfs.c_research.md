# File Research: sources/os/linux/linux-stable/fs/nsfs.c

## Summary
Implements `nsfs`, the pseudo-filesystem backing namespace file descriptors, `/proc/<pid>/ns/*` paths, namespace ioctls, namespace export file handles, and stashed namespace dentries.

## Main APIs
- Path/open helpers: `nsfs_get_root()`, `ns_get_path_cb()`, `ns_get_path()`, `open_namespace_file()`, `open_namespace()`, `open_related_ns()`.
- Ioctls: namespace owner/parent/type/id queries, pid translation queries, mount namespace info, next/previous mount namespace iteration.
- Identification helpers: `ns_get_name()`, `proc_ns_file()`, `ns_match()`, `is_current_namespace()`.
- Export operations: `nsfs_encode_fh()`, `nsfs_fh_to_dentry()`, export open/permission hooks.
- Init: `nsfs_init()`.

## Behavior
Namespace files are represented by stashed dentries and inodes whose private data is `struct ns_common`. Opening a namespace consumes or transfers namespace references into a path/file. Ioctls expose related namespaces, namespace IDs, owner uid for user namespaces, pid mappings for pid namespaces, and extensible mount namespace metadata. Export file handles encode namespace id, type, and inode number and can resolve back to dentries through the namespace tree with permission checks.

## State and Synchronization
The singleton `nsfs_mnt` hosts all namespace dentries. Inode eviction drops active namespace references and calls namespace-specific put. File-handle lookup uses RCU namespace-tree lookup and then obtains a namespace reference unless inactive. Mount namespace iteration can return a new fd plus optional info struct.

## Risks
Namespace handles are security-sensitive. `nsfs_fh_to_dentry()` restricts access to namespaces outside the caller’s view unless `may_see_all_namespaces()` permits it, and pid namespace handles reject dead current pid namespaces. Extensible ioctl size handling must preserve backward and forward compatibility.
