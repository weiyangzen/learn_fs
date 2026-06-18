# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree.c

Core SMB tree/share connection object management. The file defines the tree state machine, connection dispatch for disk/print/IPC shares, access checks, feature discovery, reference management, disconnect/deallocation, odir lookup, and enumeration/netinfo support.

`smb_tree_connect` applies a server threshold guard and calls `smb_tree_connect_core`. The core path lowercases the requested path, extracts and validates the share name, looks up the kernel share, rejects the print pseudo-share by name, enforces SMB3 encryption requirements when configured, and dispatches by share type to disk, IPC, or print handlers.

Disk tree connection validates service type, requires a configured root node, applies access checks, waits for durable-handle import to complete, builds optional-support flags for CSC/ABE/DFS/short names, allocates a tree, optionally invokes share exec-map hooks, and returns the TID. Print connection performs similar service/path/access handling with print enablement and pathname lookup. IPC connection validates service type, applies anonymous restrictions, and allocates a tree without an `snode`.

Access control combines anonymous/guest/admin-share checks, host-based share access, and share ACL access. Share ACL lookup uses `.zfs/shares/<share>` under the filesystem root when present; failures generally fall back to full access. Autohome shares grant only the owning UID.

`smb_tree_alloc` obtains a TID, gathers filesystem attributes for disk/print shares, initializes FID/ODID pools and open file/directory lists, sets state/refcount/access/resource metadata, records owner user references, applies read-only access masking, references the share root node, inserts into the session tree list, and increments server/session counters. `smb_tree_release` flushes deferred ofile/odir deletion queues, decrements references, and posts disconnected zero-ref trees for deferred deallocation. `smb_tree_dealloc` removes the tree from the session list, frees ID pools, releases root node and owner user, destroys locks/lists, and returns the object to cache.

`smb_tree_getattr`, `smb_tree_get_creation`, `smb_tree_get_volname`, and `smb_tree_get_flags` derive volume/create time, filesystem type, encryption setting, and capability flags such as ACLs, Unicode-on-disk, quotas, sparse, streams, readonly, DFS root, CATIA, continuous availability, oplocks, mount traversal, short names, case behavior, dirent flags, and ACL-on-create.

Other utilities include tree hold/internal hold, connected-state tests, PID-based close of files and searches, remote file close by unique ID, odir lookup with UID ownership enforcement, share connection logging, exec upcall metadata setup, and tree netconnect info encoding for user-space RPC consumers.
