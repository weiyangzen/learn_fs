# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvnops.c

## Purpose

`prvnops.c` is the illumos procfs vnode operation implementation. It maps VFS calls on `/proc`, `/proc/self`, `/proc/<pid>`, process files, LWP files, fd/object/path/contract directories, and old procfs compatibility files onto live kernel process, thread, address-space, file-descriptor, credential, contract, and control state.

The exported operation table is `pr_vnodeops_template`. The file is both namespace construction logic for procfs and the read/write/access layer for process observability and control.

## Main Interfaces

Important VOP entry points are `propen`, `prclose`, `prread`, `prwrite`, `prioctl`, `prgetattr`, `praccess`, `prlookup`, `prcreate`, `prreaddir`, `prreadlink`, `prinactive`, `prcmp`, `prrealvp`, and `prpoll`.

The file dispatches reads through `pr_read_function[]` and, when `_SYSCALL32_IMPL` is present, `pr_read_function_32[]`. It dispatches directory lookup and readdir through `pr_lookup_function[]` and `pr_readdir_function[]`.

Major helpers include `prgetnode`, `prfreenode`, `prfreecommon`, `prlwpnode`, `rebuild_objdir`, `obj_entry`, `pr_list_unlink`, `prreadlink_lookup`, and many per-file read routines such as `pr_read_status`, `pr_read_lstatus`, `pr_read_psinfo`, `pr_read_map_common`, `pr_read_fdinfo`, `pr_read_priv`, `pr_read_xregs`, and their 32-bit variants.

## Behavior And Data Flow

Opening procfs files validates the target process with `pr_p_lock()` or `prlock()`, tracks writer and self-writer counts in `prcommon_t`, enforces exclusive procfs writer semantics, and performs file-specific setup such as `hat_startstat()` for pagedata files. Closing reverses these counts, frees page-stat state, notifies waiters, and runs last-close behavior such as cancelling watchpoints, clearing trace masks, applying run-on-last-close, or killing the target process.

Reads are structured snapshots of live kernel state. Process and LWP status, psinfo, usage, credentials, privileges, secflags, sigactions, auxv, memory maps, watchpoints, xregs, SPARC register windows, file-descriptor info, and old procfs address-space reads all follow type-specific locking rules. Many routines allocate result buffers outside or around `p_lock` to avoid sleeping while holding process locks.

Writes are limited to address-space/process pseudo-files, control files, and `lwpname`. Control writes are delegated to `prwritectl()` or `prwritectl32()`. Address-space writes use `prusrio()`. LWP name writes require a complete bounded NUL-terminated printable string.

`prgetattr()` manufactures vnode attributes for procfs pseudo-files, with special handling for underlying object/fd/current-root vnodes, dynamic directory sizes, 32-bit caller structure sizes, address-space map sizes, fdinfo size calculation, pagedata sizing, contract links, and architecture-specific files.

## Namespace Model

`prlookup()` routes directory lookups by procfs node type. `/proc` numeric entries create or reuse process directory vnodes after PID visibility and `secpolicy_basic_procinfo()` checks. `/proc/<pid>` static entries come from `piddir[]`; `/proc/<pid>/lwp/<lwpid>` entries come from `lwpiddir[]`; fd/fdinfo/path/object/contract/template directories are generated dynamically from the target process.

`pr_readdir_*()` functions emit matching directory contents. Top-level `/proc` walks the proc table filtered by zone and policy. Object/path directories rebuild or consult address-space object directories. fd/fdinfo directories walk `uf_info_t`. LWP directories walk `p_lwpdir`. Contract directories use `contract_plookup()`.

The file supports procfs "wormholes" for `fd`, `cwd`, `root`, and object nodes by storing `pr_realvp` and sometimes returning or traversing underlying filesystem vnodes. `VTRAVERSE` is deliberately required for these cases to avoid misleading VFS path-name caching.

## Locking And Lifetime

The implementation depends on a specific lock order around `pr_pidlock`, `pidlock`, `p_lock`, address-space locks, file-table locks, `pr_mutex`, `prc_mutex`, and poll locks. It repeatedly drops `p_lock` before operations that may sleep, perform I/O, touch user memory, grab address-space locks, or call into VFS.

`prgetnode()` allocates procfs vnodes and initializes type-specific mode, vnode type, file arrays, old-proc compatibility nodes, and common state. `prinactive()` unlinks vnodes from process/LWP lists, clears parent file arrays, releases underlying vnodes and contracts, and frees `prnode_t`/`prcommon_t` state when references reach zero.

## Security And Compatibility

`praccess()` enforces readonly mounts, owner/root semantics, process credential permission checks, executable readability checks for sensitive files, fd open-mode limitations, and special world-readable files such as `psinfo`, `lpsinfo`, `lwpsinfo`, and usage files.

The file has extensive compatibility behavior: old process and LWP pseudo-files, old pagedata reads, 32-bit structure exports, `EOVERFLOW` for 32-bit callers inspecting 64-bit targets, `PR_OFFMAX`, old directory write compatibility, x86 LDT support, and SPARC-only register files.

## Dependencies

This file depends on procfs internals in `fs/proc/prdata.h`, process and LWP state in `sys/proc.h`, procfs control code in `prioctl.c`, VM/address-space interfaces, HAT pagedata statistics, generic filesystem helpers, contract APIs, VFS/vnode APIs, credential and privilege policy helpers, polling, and architecture-specific register support.

## Research Notes

This is a high-risk procfs boundary file because it exposes live kernel process state through VFS while racing process exit, exec, LWP creation/destruction, file-table changes, address-space mutation, poll notification, and zone visibility. Important audit areas are lock dropping around process lifetime, `pr_realvp` traversal behavior, old-proc compatibility paths, 32-bit conversion sizes, fd/path object lookup races, last-close side effects, and signature-sensitive return codes such as `ENOENT`, `EAGAIN`, `EBUSY`, `EOVERFLOW`, and `EBADRPC`.
