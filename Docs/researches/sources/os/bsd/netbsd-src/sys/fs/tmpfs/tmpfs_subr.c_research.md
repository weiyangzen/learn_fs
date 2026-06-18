# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_subr.c

Read completely: 1239 lines.

This is tmpfs’s core lifecycle and helper implementation. It initializes vnodes for tmpfs nodes, loads existing nodes through vcache, creates new nodes, frees nodes, constructs directory entries and files, attaches/detaches dirents, handles directory lookup and cached hints, manages directory sequence cookies, emits readdir entries, resizes regular files, and implements chmod/chown/chflags/chsize/chtimes/update helpers.

Regular files use UVM anonymous objects; `tmpfs_reg_resize` adjusts the UVM object size, zeroes truncated partial pages, drops swap backing for shrinks, and updates tmpfs memory accounting for page count changes. Directories maintain real dirents for children and virtual `.`/`..` entries through reserved cookies. Link count drives node lifetime, with vnode reclaim destroying unlinked nodes.

Important interactions: called by mount creation, vnode operations, rename callbacks, and unmount teardown. It selects vnode operation vectors for regular/directory/symlink/socket, FIFO, and special-device nodes.

Security/reliability notes: careful ENOSPC unwind paths exist for symlink target, dirent, and vnode creation. Directory cookie allocation has a first incremental range and a vmem-managed overflow range. Holdcount/reclaimed bits protect nodes during file-handle lookup and deferred destruction.
