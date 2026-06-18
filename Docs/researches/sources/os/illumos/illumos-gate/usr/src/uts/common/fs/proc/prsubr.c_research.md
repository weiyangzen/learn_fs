# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prsubr.c

## Purpose

`prsubr.c` is the core procfs support library. It supplies process/LWP selection, procfs vnode lifetime hooks, process locking, status/ps/usage formatting, memory-map and page-data generation, fdinfo generation, watchpoint bookkeeping, credential/privilege export, and 32-bit conversion helpers.

## Lifecycle and Notification

Key lifecycle hooks:

- `prnotify()` wakes waiters and pollers on procfs state changes.
- `prfree()` clears procfs process references when a process leaves the process table.
- `prexit()` marks traced process files as destroying and tears down watchpoints.
- `prlwpexit()` and `prlwpfree()` update LWP-specific procfs vnode state as LWPs exit or are reaped.
- `prexecstart()` blocks procfs operations during exec with `P_PR_EXEC`.
- `prexecend()` clears exec blocking and refreshes data model/TID metadata on open procfs nodes.
- `prrelvm()` removes watched areas/pages before address-space destruction.
- `prinvalidate()` invalidates sensitive procfs vnodes after set-id or unreadable exec events while preserving public information files.

## Process Locking

The central protocol is:

- `pr_p_lock()` takes `pr_pidlock`, finds the process through procfs common state, takes `p_lock`, waits for `P_PR_LOCK` to clear, then sets `P_PR_LOCK`.
- `prlock()` wraps `pr_p_lock()`, handles zombie/exiting/lwp-invalid cases, rejects invalidated nodes, and waits for in-progress execs.
- `prunmark()` clears `P_PR_LOCK` and wakes waiters.
- `prunlock()` calls `prunmark()` and drops `p_lock`; if the target was killed, it attempts to make it runnable.
- `prbarrier()` is used by process-owned paths to wait until procfs is no longer controlling the process.

This locking design prevents LWPs from disappearing while procfs inspects or controls them, and it establishes the lock ordering used by the rest of procfs.

## LWP Selection

`prchoose()` selects the representative LWP for process-wide operations. Its precedence is semantically important:

1. Agent LWP, if present.
2. On-processor LWP.
3. Runnable LWP.
4. Sleeping LWP.
5. Job-control stopped LWP.
6. Directed job-control stop.
7. Event-of-interest stop.
8. DTrace/requested stops.
9. Hold/suspended states.
10. Zombie fallback.

The function returns the chosen thread with its dispatcher lock held.

## Status and psinfo Generation

The file builds both modern and 32-bit status structures:

- `prgetstatus()` / `prgetstatus32()` fill process-wide `pstatus`.
- `prgetlwpstatus()` / `prgetlwpstatus32()` fill detailed LWP status, including stop reason, signal state, syscall args, rval/errno on syscall exit, fault info, registers, FP registers, and microstate time.
- `prgetpsinfo()` / `prgetpsinfo32()` fill `psinfo`.
- `prgetlwpsinfo()` / `prgetlwpsinfo32()` fill lightweight `lwpsinfo`.

It sanitizes zone-crossing signal info, maps kernel thread states to user-visible process states, exposes only selected process flags, and zeroes unrepresentable fields in 32-bit views.

## Memory Maps and Page Data

Memory-map support includes:

- `prnsegs()` counts visible map ranges, splitting segments by effective protection.
- `break_seg()` identifies the process heap segment.
- `prgetmap()` / `prgetmap32()` emit map entries with address, size, offset, protections, shared/noreserve/anon/break/stack/ISM/SHM flags, object names, and SysV SHM IDs.
- `prpdsize()` / `prpdsize32()` compute page-data file sizes.
- `prpdread()` / `prpdread32()` emit page-data headers and per-map page residency data.
- `prgetxmap()` / `prgetxmap32()` emit extended map entries including HAT page size plus RSS/anonymous/locked page counts.

The helper `pr_getsegsize()` trims segment sizes for regular files, ISM backing sizes, and `/dev/null`-style virtual reservations. `pr_getprot()` computes contiguous ranges of effective protection, handling per-page protections and `MAP_NORESERVE` materialization through the internal `prpagev_t` vector.

## Chained I/O Buffers

The `pr_iol_*()` helpers implement generic chained kernel buffers for variable-size procfs output:

- `pr_iol_initlist()` initializes a list with a bounded first buffer.
- `pr_iol_newbuf()` allocates space for one item and appends 64 KiB buffers as needed.
- `pr_iol_copyout_and_free()` copies the chain to user memory.
- `pr_iol_uiomove_and_free()` feeds the chain through a `uio_t`.
- `pr_iol_freelist()` releases without copying.

These helpers are shared by map, fdinfo, and other variable-output paths.

## FD Info

FD inspection support is built around:

- `pr_getf()` safely obtains a referenced `file_t` from another process while avoiding a procfs close-path lock inversion through bounded `mutex_tryenter()` retries.
- `pr_releasef()` drops that procfs-held file reference without always going through full close logic.
- `prgetfdinfosize()` computes `/proc/<pid>/fdinfo/<fd>` size, including misc trailers.
- `prgetfdinfo()` fills `prfdinfo_t` with offsets, stat attributes, lock info, peer credentials, paths, socket/TLI names, and socket options.

Socket/TLI helpers include `pristli()`, `prfdinfotlisockopt()`, and `prfdinfosockopt()`. Door pathname handling walks mounted namenodes.

## Usage Accounting

Usage helpers include:

- `estimate_msacct()` and `disable_msacct()`, now mostly compatibility shims because microstate accounting is effectively always available.
- `prgetusage()` for one LWP.
- `praddusage()` to aggregate one LWP into a process total.
- `prscaleusage()` to convert unscaled high-resolution accounting.
- `prcvtusage()` / `prcvtusage32()` to convert high-resolution internal usage to exported structures.

The accounting paths adjust for current dispatch-queue wait time and current microstate time, with bounded retries for timebase races.

## Watchpoints

Watchpoint state is split into watched areas and watched pages:

- `set_watched_area()` inserts or updates an AVL-sorted watched range, enabling watchpoints on all LWPs when the first watch appears.
- `clear_watched_area()` removes an exact watched range and disables watchpoints when the last one disappears.
- `pr_free_watchpoints()` frees process watched-area structures.
- `pr_free_watched_pages()` restores original protections and frees address-space watched-page state.
- `set_watched_page()` and `clear_watched_page()` maintain per-page read/write/exec watch counters and queue protection updates through `p_wprot`.
- `getwatchprot()` restores original protections when procfs map readers report pages affected by watchpoint protection changes.

## Credentials and Privileges

The file exports process security state through:

- `prgetcred()`
- `prgetsecflags()`
- `prgetprivsize()`
- `prgetpriv()`

These use credential locks where needed and rely on common privilege conversion routines.

## Compatibility Helpers

Under `_SYSCALL32_IMPL`, the file provides 32-bit status, psinfo, map, page-data, and xmap variants, plus structure conversion helpers `lwpsinfo_kto32()` and `psinfo_kto32()`. Pointer-sized fields that cannot be represented are either omitted, zeroed, or copied only for ILP32 targets.
