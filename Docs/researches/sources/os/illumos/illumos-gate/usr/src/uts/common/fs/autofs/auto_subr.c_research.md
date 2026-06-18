# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_subr.c

## Purpose

`auto_subr.c` contains the main support routines for the illumos autofs kernel filesystem. It coordinates in-kernel autofs nodes with per-zone `automountd` instances through doors, creates worker threads for mount requests and periodic unmounting, validates untrusted daemon action lists, manages fnnode lifetimes, and implements bottom-up autofs subtree unmount logic.

## File Shape

- Size: 2,654 lines, 69,593 bytes.
- SHA-256: `1f3340643356767defff044a22d978070145a525186947c73f16a8c099048788`.
- Major exported/support functions include `auto_unblock_others()`, `auto_wait4mount()`, `auto_lookup_aux()`, `auto_new_mount_thread()`, `auto_calldaemon()`, `auto_makefnnode()`, `auto_freefnnode()`, `auto_disconnect()`, `auto_enter()`, `auto_search()`, `unmount_subtree()`, `unmount_tree()`, `auto_do_unmount()`, `auto_nobrowse_option()`, and `auto_log()`.

## Core Behavior

- Synchronizes mount and lookup operations with `MF_INPROG`, `MF_LOOKUP`, `MF_WAITING`, and `fn_cv_mount`; interrupted mounts are converted to `EAGAIN` so another thread can retry.
- `auto_calldaemon()` marshals requests with XDR, calls the zone-local automountd door via `door_ki_upcall_limited()`, retries hard calls when the daemon is unavailable, handles door revocation and buffer overflow responses, decodes response XDR, and respects zone shutdown.
- `auto_lookup_request()` and `auto_mount_request()` build autofs protocol requests from `fninfo_t`, including direct-map key handling, subdir, options, and caller UID.
- `auto_mount_thread()` is the worker entry point for mount triggers: it asks automountd for actions, performs them, records `fn_error`, wakes waiters, and releases held vnode/credential/name state.
- `auto_perform_actions()` validates every daemon-provided action before executing it. It accepts only autofs mount actions with relative `.`/`./...` directories, no parent traversal, expected path strings, and correct `autofs_args`; invalid action lists from a zone-local daemon are rejected with a global warning.
- Kernel-created autofs trigger mounts are marked with `MF_IK_MOUNT`; trigger lists and saved action lists allow subordinate autofs trigger nodes to be unmounted and remounted as a unit.
- `auto_makefnnode()`, `auto_enter()`, `auto_search()`, `auto_disconnect()`, and `auto_freefnnode()` implement the in-memory autofs directory tree, odd inode allocation, credential-sensitive `thisuser` symlink matching, reference/link counting, and vnode lifecycle.
- `unmount_subtree()` performs a timestamp-marked depth-first traversal over fnnode children, trigger lists, and mounted autofs roots so nodes are processed bottom-up.
- `try_unmount_node()` checks reference counts, timeouts, in-progress flags, trigger busy state, and mount coverage before unmounting. It remounts triggers on failure when necessary.
- `auto_do_unmount()` is the per-zone periodic unmount scheduler. It waits with zone-shutdown awareness, limits concurrent unmount worker threads, and exits cleanly during zone teardown.

## Dependencies And Contracts

- Depends on `sys/fs/autofs.h` structures (`fnnode_t`, `fninfo_t`, `autofs_globals`, flags), autofs protocol XDR routines from `auto_xdr.c`, and VFS/vnode primitives.
- Uses zone-specific storage and zone-local door handles established by `AUTOFS_SETDOOR`.
- Assumes each zone owns its own autofs tree and automountd. Cross-zone triggers are disallowed elsewhere, and this file assumes most daemon communication is for the current zone unless forced global-zone cleanup is in progress.
- Uses `domount()`, `dounmount()`, `lookuppnvp()`, `VFS_ROOT()`, `vn_mountedvfs()`, vnode locks, and GFS/NFS-related interfaces indirectly through mount actions.

## Maintenance Notes

This file contains several explicit CPR/suspend-safety caveats because worker paths may block in RPC, memory allocation, VFS calls, or network filesystems. Lock ordering is delicate: fnnode mutexes, fnnode rwlocks, vnode VFS locks, and vnode reference counts are all used to avoid races with lookup, mount, unmount, and inactive paths. Treat daemon-provided action validation as a security boundary because non-global zones run their own automountd instances.
