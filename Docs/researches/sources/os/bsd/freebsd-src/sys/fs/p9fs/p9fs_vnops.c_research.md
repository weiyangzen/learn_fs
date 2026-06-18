# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vnops.c

## Purpose

Implements FreeBSD vnode operations for the 9P filesystem client. It translates VFS operations into 9P client requests, maintains p9fs node/fid state, updates vnode attributes and pager size, and connects path lookup, creation, I/O, directory iteration, removal, rename, links, symlinks, and VM paging to the lower `p9_client_*` protocol layer.

## Main Entry Points

The exported VOP vector `p9fs_vnops` registers handlers for lookup, open/close, access, getattr/setattr, create/mknod/mkdir, read/write, remove/rmdir, readdir, strategy, symlink, rename, link, readlink, putpages, inactive, reclaim, delayed setsize, and pathconf.

Node lifetime is handled by:
- `p9fs_cleanup()`: removes a vnode from the hash/session lists, purges namecache entries, destroys the VM object, removes all fids, and destroys the `p9fs_node`.
- `p9fs_reclaim()`: calls cleanup on vnode reclaim.
- `p9fs_inactive()`: recycles nodes marked `P9FS_NODE_DELETED`.

Lookup and creation:
- `p9fs_lookup()` walks the server with `p9_client_walk()`, validates cached vnodes against returned qids and fresh attrs, enforces read-only/delete/rename and sticky-directory rules, and calls `p9fs_vget_common()` for new vnode materialization.
- `create_common()` clones the parent fid, sends `p9_client_file_create()`, walks back to the new child, creates the vnode, and retains the create-open fid as a `VOFID` when appropriate.
- `p9fs_create()`, `p9fs_mkdir()`, and `p9fs_mknod()` are thin mode translators around `create_common()`.

Attributes and permissions:
- `p9fs_reload_stats_dotl()` and `p9fs_stat_vnode_dotl()` fetch 9P2000.L attrs, update inode fields, vnode type, qid version, modification flag, and pager size.
- `p9fs_getattr_dotl()` exports inode fields as `struct vattr`.
- `p9fs_setattr_dotl()` implements chmod/chown/truncate/time changes, builds `p9_iattr_dotl`, calls `p9_client_setattr()`, and rolls back size on failed truncation.
- `p9fs_access()` combines read-only filesystem checks with `vaccess()`.

I/O:
- `p9fs_open()` finds or clones a fid, sends `p9_client_open()`, tracks `v_opens`, creates a vnode object for regular files, and caches open fids per credential/mode.
- `p9fs_close()` decrements open fid counts; final clunk happens during node cleanup.
- `p9fs_read()` and `p9fs_write()` obtain an open fid, use a UMA I/O buffer, loop over `p9_client_read()`/`p9_client_write()`, and move data through `uio`.
- `p9fs_strategy()` and `p9fs_doio()` service buffer-cache I/O through synthetic `uio` structures.
- `p9fs_putpages()` maps dirty VM pages into a pbuf and writes them synchronously via `VOP_WRITE()`.

Directory and namespace operations:
- `p9fs_readdir()` reads 9P directory data with `p9_client_readdir()`, parses `struct p9_dirent`, and emits FreeBSD `struct dirent`.
- `remove_common()`, `p9fs_remove()`, and `p9fs_rmdir()` call `p9_client_unlink()`, remove non-open fids, purge caches, remove from vnode hash, and mark deleted.
- `p9fs_symlink()`, `p9fs_link()`, `p9fs_readlink()`, and `p9fs_rename()` map VFS namespace operations to 9P symlink, hardlink, readlink, and renameat helpers.
- `p9fs_pathconf()` returns `_PC_NAME_MAX` from `p9_client_statfs()` when available and conservative path/symlink limits otherwise.

## Integration Points

This file depends on `p9fs_get_fid()`, `p9fs_fid_add()`, `p9fs_fid_remove_all()`, `p9fs_vget_common()`, `p9fs_destroy_node()`, and lower `p9_client_*` request helpers. It owns the VFS-facing half of p9fs and cooperates with mount/session code through `struct p9fs_session`, vnode hash membership, and the session node list.

## Risks and Review Notes

Name lookup temporarily null-terminates `cn_nameptr`; all paths restore the saved byte, so error exits around that pattern are important review targets.

Open fid reuse is credential/mode sensitive and deliberately retains create-open fids to avoid failing later opens on newly created `000` files.

`p9fs_write()` moves data from the user `uio` before all server writes complete; if the server accepts only a partial inner write, the user-visible `uio` offset can advance farther than the actual server offset. This is worth targeted write-shortening tests.

Several size updates derive from current `uio` state after loops. Truncate/write/page-write behavior should be tested around partial writes, EOF extension, and concurrent server-side file changes.
