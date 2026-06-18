# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/acct.c

This file implements the `acct(2)` process-accounting system call and the weak-stub `acct()` hook called from process exit. Accounting is virtualized per zone: each zone has an `acct_globals` containing the reusable accounting record buffer, a lock, and the held vnode for the accounting file. A global list of all zone accounting states allows the kernel to reject reuse of an accounting file or filesystem already used by another zone.

Module initialization creates the global list and lock, registers a zone key with init/shutdown/fini callbacks, and installs the `acct(2)` syscall. The module refuses unload in `_fini()` because unloading after accounting is enabled would silently stop process-exit accounting.

`sysacct()` checks `secpolicy_acct()`, then either disables accounting for the caller’s zone when `fname == NULL`, or opens a new regular file for writing. It prevents accounting to non-regular files, maps `EISDIR` to `EACCES` for SVID compatibility, and uses `acct_find()` under `acct_list_lock` to detect vnode or filesystem reuse. Switching files swaps the new vnode into the zone state while closing and releasing the old one outside the per-zone lock as needed.

`acct_find()` performs deep vnode comparison through `VOP_REALVP()` so loopback/shadow vnodes compare to the same underlying file. With `compare_vfs` true it detects whether a mounted filesystem contains any active accounting file; `acct_fs_in_use()` exposes that check to other kernel code.

`acct()` runs during process exit. It copies command name, start time, compressed user/system/elapsed time, memory, I/O counts, uid/gid, controlling tty, status, and accounting flags into the zone’s `acctbuf`. It appends the record to the accounting vnode with `vn_rdwr()` under the per-zone lock, bounded by `MAXOFF32_T` because traditional accounting tools are not large-file aware. If the append fails or is short, it restores the previous file size to avoid leaving a corrupt partial record.

The important dependencies are zone-specific storage, vnode open/close/read-write operations, process resource accounting fields, credentials, and the legacy `comp_t` pseudo-floating format. Correctness concerns are lock ordering between global and per-zone accounting locks, avoiding held vnodes during zone shutdown, and preventing partial record corruption.
