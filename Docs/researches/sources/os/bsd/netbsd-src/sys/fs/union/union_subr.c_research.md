# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_subr.c

Read completely: 1234 lines.

Provides support routines for the legacy union filesystem: global node-cache management, vnode/node allocation, vnode loading, lock-sharing updates, size tracking, copy-up, shadow directory and whiteout creation, directory stack caching, rmdir emptiness checks, and the global readdir hook.

A global hash table maps `(uppervp, lowervp, mount)` combinations to `union_node` instances. `union_init()`, `union_reinit()`, and `union_done()` manage this table and clear `vn_union_readdir_hook`. `union_allocvp()` finds or creates union nodes, handles type mismatches by discarding the lower vnode, stores saved component names for later copy-up, and uses `vcache_get()` to attach/reuse vnodes. `union_loadvnode()` initializes the union vnode, shares the active underlying vnode’s interlock, UVM object lock, and kqueue list, marks roots, and seeds size state.

`union_newupper()` and `union_newlower()` update backing vnodes and hash membership; `union_newupper()` performs a lock transfer from the union vnode to the new upper vnode and rebinds VM/kqueue state. `union_newsize()` updates UVM-visible size based on upper-preferred size changes. `union_copyfile()` streams data from lower to upper in `MAXBSIZE` chunks, while `union_copyup()` creates an upper shadow file, optionally copies contents and permissions, closes/reopens lower/upper vnodes to preserve open accounting, and installs the upper vnode.

Directory support includes `union_mkshadow()` for upper shadow directories, `union_mkwhiteout()` for whiteouts, `union_dowhiteout()` policy checks, `union_dircache()`/`union_diruncache()` for walking a directory stack, `union_check_rmdir()` for checking lower entries hidden by upper whiteouts or entries, and `union_readdirhook()` for switching a `getdirentries` stream from upper to lower after the upper directory is exhausted.

Risks and notes: copy-up comments acknowledge ignored close/open errors and imperfect credential/mode handling. Shadow directories may be attempted even on read-only union mounts. The directory-cache table panics if sizing assumptions fail. `union_removed_upper()` intentionally leaves stale upper/lower pointers after removing a node from the hash so current holders can drain safely. The readdir hook depends on global `vn_union_readdir_hook`, so only one union-style hook can be active.
