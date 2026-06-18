# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exec.c

## Purpose

`exec.c` implements the generic illumos kernel `exec(2)` path: syscall entry, executable lookup, exec-switch dispatch, permission and privilege handling, process state replacement, VM/address-space replacement, stack construction, auxiliary-vector string placement, and exec-module lookup.

It is central process lifecycle code, with heavy coupling to VFS/vnodes, credentials/privileges, `/proc`, brands/zones, DTrace, resource controls, doors, schedctl, timers, lwp management, and VM segment mapping.

## Main Entry Points

- `exece()` (`exec.c:134`) is the syscall wrapper. It validates flags and supports `EXEC_DESCRIPTOR`, where the `file` argument is interpreted as an fd. For descriptor exec it obtains a vnode with `fgetstartvp()`, tries to copy `vp->v_path`, and falls back to `/dev/fd/<fd>` if no cached path exists.
- `exec_common()` (`exec.c:197`) performs pathname or vnode setup, brand policy checks, `/proc` exec-start notification, signal hold adjustments, `pfexec` integration, and calls `gexec()`. On success it completes process-state reset and returns to the new image.
- `gexec()` (`exec.c:637`) performs generic executable validation, opens the vnode, reads magic bytes, finds the exec handler, computes credential/setid/secflag transitions, invokes the format-specific `exec_func`, and commits new credentials and tracing state.
- `exec_args()` (`exec.c:2002`) builds the new process stack, terminates other LWPs, tears down exec-sensitive state, replaces the address space, sets stack/heap metadata, and installs optional 64-bit stack guard mapping.

## Exec Flow

`exec_common()` rejects `/proc` agent LWP execs, enforces brand transitions, and calls `prexecstart()` while temporarily holding default-ignored signals. It either uses a supplied vnode or resolves the user pathname with `pn_get()` and `lookuppn()`, preserving both the executable pathname and the containing directory for `p_execdir`.

Before format dispatch, it enforces `secpolicy_basic_exec()`, rejects execution from attribute directories in the specific current-directory case, stores accounting command text, and optionally calls `pfexec_call()` when `PRIV_PFEXEC` is set. It initializes default stack/data protections, fires DTrace `proc:::exec`, applies process branding if needed, and calls `gexec()`.

After `gexec()` succeeds, the old process image is considered replaced. `exec_common()` frees floating-point state and context ops, clears accounting fork state and DTrace predicate cache, clears contract templates, updates `p_execdir`, resets signal stack/signal disposition metadata, refreshes saved rlimits, clears profiling, closes `FD_CLOEXEC` descriptors via `close_exec()`, clears native brand state if requested, calls `setregs()`, marks the vnode `VVMEXEC`, and rebuilds the process LWP directory/hash so the now-single-threaded process has LWP id 1.

## Permission, Format, and Credential Handling

`execpermissions()` (`exec.c:1214`) gets mode/uid/gid/size attributes, checks `VEXEC`, verifies regular file or `/proc` object file, rejects `VFS_NOEXEC`, and requires at least one execute mode bit. For traced processes it may also require read permission or arrange `/proc` invalidation.

`gexec()` opens the executable vnode with `VOP_OPEN()`, reads `MAGIC_BYTES`, resolves the handler with `findexec_by_hdr()`, and holds the exec switch entry with `hold_execsw()`. It calculates setuid/setgid/forced privilege behavior via `execsetid()` and promotes inheritable secflags with `secflags_promote()` before calling the format-specific `exec_func`.

`execsetid()` (`exec.c:1111`) evaluates `VFS_NOSETUID`, `VSUID`, `VSGID`, forced privileges for setuid-root programs, privilege-aware reset needs, inherited/limit/permitted privilege relationships, MAC awareness flags, and ptrace compatibility. It returns flags indicating whether credentials, privilege sets, MAC flags, or setuid protections must change.

On successful level-0 exec, `gexec()` closes the previous executable vnode, installs new credentials on both process and current thread, updates saved uid/gid, sets `SNOCD|SUGID` when privilege increased or effective ids differ, updates per-uid process counts if real uid changed, handles `/proc` invalidation, and sends `SIGTRAP` for ptrace compatibility.

## Exec Switch Management

- `allocate_execsw()` installs an exec switch name and magic bytes into the global `execsw` table.
- `findexecsw()`, `findexec_by_hdr()`, and `findexec_by_magic()` locate handlers by magic bytes.
- `hold_execsw()` acquires the handler reader lock and autoloads the corresponding `exec` module with `modload()` until `LOADED_EXEC()` is true.

The exec switch lock is intentionally held across `exec_func()` and released immediately after the format-specific handler returns.

## VM and Segment Mapping

`execmap()` (`exec.c:1261`) maps file-backed executable sections or copies them into anonymous mappings. It page-aligns addresses and offsets, validates user ranges, uses `VOP_MAP()` for page-mapped segments, optionally prefaults small segments, and adjusts memory deficit accounting when not prefaulting.

For zero-fill-on-demand trailing data, it carefully handles partial pages. If the last page lacks write permission, it temporarily adds `PROT_WRITE`, zeroes with `uzero()` under `on_fault()`, and restores protections. Remaining zfod space is mapped with `segvn_create`, using large-page mapping hints when `szc` is set.

`setexecenv()` updates process brk/bss metadata and swaps `p_exec` vnode references.

## Stack Construction

The stack-building helpers use an in-kernel staging buffer where strings grow upward from `stk_base` and string offsets grow downward from the top.

- `stk_add()` copies strings from user or kernel space into the staging buffer.
- `stk_getptr()` and `stk_putptr()` handle native versus 32-bit pointer models.
- `stk_copyin()` copies interpreter arguments, original argv, environment, optional `pfexec`-scrubbed environment variables, and aux-vector strings into the staging buffer.
- `stk_copyout()` writes `argc`, argv pointers, envp pointers, string data, and aux-vector string addresses to the new user stack. It also records `u_argc`, `u_argv`, `u_envp`, and `u_psargs`.

`exec_get_spslew()` supplies stack-pointer ASLR when `PROC_SEC_ASLR` is enabled; on `sun4v`, it can provide cache-coloring skew even without ASLR.

`exec_args()` selects native or ILP32 stack model, repeatedly grows the staging buffer until arguments fit or `NCARGS`/`NCARGS32` is exceeded, then calls `exitlwps()` to make the process single-threaded. It revokes process doors, cleans schedctl/DTrace/lwpchan/timer state, audits arguments, uses pool barriers around `relvm()`, resets process address-space metadata, allocates a fresh `as`, joins the executable vnode’s shared region domain with `hat_join_srd()`, copies out the new stack, and for 64-bit processes maps a `seg_hole` stack guard.

## Error and Fatality Boundaries

Before old VM destruction, errors unwind with errno and restore signal holds, exec-start state, secflags, credentials, vnode opens, and brand state as appropriate. After `relvm()` in `exec_args()`, comments state errors are fatal to the execing process; callers must treat `-1`/post-destruction failure as requiring process death.

## External Interactions

This file is tightly integrated with:

- VFS/vnode operations: `lookuppn()`, `VOP_ACCESS()`, `VOP_GETATTR()`, `VOP_OPEN()`, `VOP_CLOSE()`, `VOP_MAP()`, `vn_rdwr()`.
- Descriptor table code in `fio.c`: `fgetstartvp()`, `close_exec()`, `falloc()`, `setf()`, `closeandsetf()`.
- Process exit/LWP code: `exitlwps()`, LWP directory/hash rebuild, `lwp_exit()` behavior on failure paths.
- VM: `relvm()`, `as_alloc()`, `as_map()`, `as_setprot()`, `segvn_create`, `seghole_create`.
- Security: privileges, secflags, setuid/setgid, `pfexec`, MAC flags, noexec stack policy.
- Observability: `/proc`, DTrace, audit, accounting.

## Research Notes

The most delicate invariants are around the boundary where the old process image is still recoverable versus after `relvm()`, credential replacement under `p_crlock`, `execsw` module locking, and keeping `/proc`/tracing semantics consistent while mutating process identity and address space.
