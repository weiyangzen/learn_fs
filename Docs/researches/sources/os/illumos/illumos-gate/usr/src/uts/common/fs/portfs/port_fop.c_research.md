# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fop.c

## Role

Implements `PORT_SOURCE_FILE`, the event-port source for file and directory change notification. It uses FEM vnode-operation hooks and FSEM filesystem unmount hooks to observe file activity, pathname identity changes, mounted-over events, and unmounts.

## Major Responsibilities

- Register file watches from user `file_obj_t`/`file_obj32_t` objects.
- Maintain a per-port `portfop_cache_t` keyed by user object pointer and pid.
- Maintain per-vnode `portfop_vp_t` lists of active/inactive watches.
- Lazily install FEM hooks on watched vnodes.
- Lazily install FSEM unmount hooks on watched filesystems.
- Deliver file events through cached `port_kevent_t` records.
- Deactivate watches after event delivery, preserving inactive entries for fast reassociation.
- Remove watches and send exception events when file identity changes.
- Clean up all per-pid and last-close file-watch state.
- Handle hard-link/name-sensitive exception behavior.

## Key Data And Structures

- `portfop_t` represents one watch: watched vnode, optional directory vnode, basename, user object pointer, pid, event mask, cached event, port cache, and state flags.
- `portfop_vp_t` is attached to `vnode_t.v_fopdata` and owns the per-vnode watch list, FEM pointer, count, oldest inactive pointer, and filesystem-watch linkage.
- `portfop_vfs_t` tracks watched vnodes for a filesystem and owns the FSEM hook state.
- `portvfs_hash` indexes watched filesystems by `vfs_t`.

## Key Functions

- `port_associate_fop()` copies in the user file object, resolves the path and directory vnode, validates vnode event support, associates the `PORT_SOURCE_FILE` source, creates or reuses a watch, and checks timestamps for immediate events.
- `port_dissociate_fop()` removes a watch owned by the current pid and returns success only if the watch was active or had a queued event removed.
- `port_fop_associate_source()` creates the per-port source cache on first use.
- `port_pfp_setup()` allocates `portfop_t` and cached event state, installs vnode/FEM and filesystem/FSEM hooks as needed, inserts the watch into port and vnode caches, and holds required vnode references.
- `port_fop_getdvp()` resolves the user pathname to vnode and directory vnode, also storing the final path component.
- `port_resolve_vp()` normalizes special mntfs and real-vnode cases.
- `port_check_timestamp()` compares supplied atime/mtime/ctime against current vnode attributes and immediately posts matching access/modified/attrib events.
- `port_fop_sendevent()` delivers events to matching watches, handles active/inactive ordering, converts non-matching hard-link exceptions to `FILE_ATTRIB`, and removes exception watches.
- `port_fop_excep()` sends exception events using fresh non-cached events, then frees the old watch.
- `port_remove_fop()` removes a watch from vnode and port caches, removes queued events, and uninstalls FEM hooks if the vnode has no remaining watches.
- `port_close_fop()` removes all watches for a closing pid and destroys the source cache on last close.
- `port_fop_unmount()` handles filesystem unmount by blocking new watches, uninstalling FSEM hooks, sending `UNMOUNTED` events to all watched vnodes, releasing holds, and removing the filesystem record.

## Hook Coverage

The FEM hook table wraps operations that can affect observed timestamps or identity, including open, read, write, map, setattr, create, remove, link, rename, mkdir, rmdir, readdir, symlink, setsecattr, and vnode event notifications.

The simple wrapper hooks call the underlying `vnext_*()` operation first and only generate events on successful completion. `port_fop_vnevent()` maps filesystem-provided vnode notifications such as rename source/destination, remove, rmdir, create, link, mounted-over, and truncate.

## Watch Lifecycle

A watch starts active at the head of the vnode list. When a normal event is sent, it becomes inactive and moves to the tail. Reassociation reactivates it, updates event/user data, removes any queued prior event, and moves it back to the active region. Exception events remove and free the watch because the watched object identity is gone or changed.

Inactive watches are retained for performance, but `port_fop_trimpfplist()` attempts to discard old inactive watches when a vnode exceeds `port_fop_maxpfps`.

## Locking

The primary lock order is `pfc_lock` followed by `pvp_mutex`. Some cleanup paths use temporary lists because exception delivery needs the reverse context and cannot safely acquire the cache lock while inside the vnode hook list traversal. Vnode references that require `VN_RELE()` are collected and released after dropping locks.

## Research Notes

This file is the most complex portfs source file because it combines user object identity, pathname lookup, vnode identity, hard-link semantics, event-port one-shot behavior, and filesystem unmount coordination. The design intentionally avoids blocking unmounts in the general case, but NFS-style filesystems are treated specially unless unmount is forced.
