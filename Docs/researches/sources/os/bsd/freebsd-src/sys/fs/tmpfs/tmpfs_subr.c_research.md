# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_subr.c

Tmpfs support implementation for the VM pager integration, memory accounting, node lifecycle, vnode lifecycle, directory indexing, readdir, whiteouts, resizing/hole punching, attribute mutation, timestamps, and initialization.

Key responsibilities:
- Creates `vfs.tmpfs` sysctls and tunables for reserved memory and percent of available memory usable by unlimited tmpfs mounts.
- Defines tmpfs directory-entry malloc type, UMA node pool, VFS SMR zone use, and dynamic VM pager type.
- Implements a tmpfs pager backed by swap objects, with callbacks for allocation, writable mapping count changes, vnode lookup, free-space accounting, page insert/remove accounting, and page-allocation admission.
- Maintains `tm_pages_used` and per-node `tn_pages` as swap/page cache state changes through pager callbacks.
- Keeps vnodes with writable mappings referenced and on the lazy list so mmap writes can update mtimes.
- Initializes and tears down the dynamic pager type and UMA node zone in `tmpfs_subr_init()` and `tmpfs_subr_uninit()`.
- Computes available memory from swap plus free pages minus a reserved threshold, and checks per-mount page limits through `tmpfs_pages_check_avail()`.
- Allocates tmpfs nodes for all supported vnode types, including parent link handling for directories, SMR-safe symlink storage, and regular-file VM object creation with tmpfs backpointers.
- Frees nodes with reference counting, detach/list removal, extended attribute cleanup, VM object flag clearing/accounting, symlink storage cleanup, mount refcount release, and SMR UMA free.
- Allocates and frees dirents, updating target node link counts.
- Allocates/reuses vnodes for nodes with `tn_vpstate` coordination, handles existing/doomed/allocating vnode races, attaches regular-file VM objects to vnodes, swaps FIFO vnode ops, and inserts vnodes into the mount queue.
- Destroys vnode-object association for reclaimed or failed vnodes, including clearing `OBJ_TMPFS_VREF` references created by writable mappings.
- Allocates new filesystem objects by creating a node, dirent, vnode, and finally attaching the dirent atomically to the parent directory.
- Implements RB-tree directory iteration with collision lists for duplicate hash cookies and a sorted duplicate index.
- Implements directory lookup by name/hash, duplicate-cookie lookup for readdir restart, attach/detach with duplicate-head conversion, and full directory destruction.
- Generates `.` and `..` dirents and emits real entries with stable `d_off` cookies, whiteout handling, readdir cache updates, access timestamp marking, and optional NFS cookie arrays.
- Implements whiteout add/remove/clear support for union mounts.
- Implements regular-file resize/truncate by zeroing partial pages, removing full pages, changing VM object size, and updating node size.
- Implements hole punching by zeroing partial boundary pages and removing full pages while returning adjusted offset/length.
- Detects dirty mmap writes by comparing VM object generation and clean generation, marking nodes modified/changed.
- Implements chflags, chmod, chown, chsize, chtimes, timestamp syncing, access/status marking, and final truncation wrapper with read-only, immutable, append-only, privilege, securelevel, and rlimit checks.
- Generates the directory RB-tree comparator and implementation.

Dependencies:
- FreeBSD VM pager, swap pager, VM object/page, vnode, mount, SMR, UMA, sysctl, random harvesting, namecache, privilege, securelevel, UIO, dirent, whiteout, and lock/refcount APIs.
- Tmpfs VFS and vnode state from `tmpfs.h`, FIFO vnode ops, and generic tmpfs vnode ops.

Notable risks:
- Pager callbacks and vnode lifecycle code cross VM/VFS locking domains; lock ordering and reference handoff are critical.
- Writable mmap tracking keeps extra vnode references through `OBJ_TMPFS_VREF`; forced unmount and reclaim paths must clear them.
- Directory cookie collision handling is intricate: normal RB entries can become duplicate heads, duplicate entries receive separate cookie values, and readdir restart depends on both RB and duplicate-index state.
- `tmpfs_free_node_locked()` may unlock the mount while deallocating VM objects, so callers must respect its boolean return contract.
- Mount/node refcounts let VM objects outlive the mount after unmount; page accounting must remain valid until the final object is gone.
- Timestamp updates are lazy and can be triggered by getattr/sync/mmap dirty generation checks.
