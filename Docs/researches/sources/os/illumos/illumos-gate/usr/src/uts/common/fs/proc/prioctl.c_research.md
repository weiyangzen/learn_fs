# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prioctl.c

## Purpose

`prioctl.c` implements the legacy ioctl-based `/proc` control interface for illumos procfs. It translates old `PIOC*` commands into modern process-control operations, exposes old-format process/LWP status structures, implements old map/page-data readers, and handles 32-bit compatibility dispatch when `_SYSCALL32_IMPL` is enabled.

## Main Entry Points

- `prioctl()` is the vnode ioctl entry point. In 64-bit syscall builds it dispatches by caller data model to `prioctl32()` or `prioctl64()`.
- `prioctl64()` is the native ioctl implementation.
- `prioctl32()` mirrors the native implementation with ILP32 structure layouts, pointer narrowing, and `EOVERFLOW` checks for LP64 targets where old 32-bit structures cannot represent target state.
- `prctioctl()` handles contract-template proc nodes (`PR_TMPL`) for `CT_TSET` and `CT_TGET`.
- `oprgetstatus()` / `oprgetstatus32()` build old `prstatus_t` / `prstatus32_t`.
- `oprgetpsinfo()` / `oprgetpsinfo32()` build old `prpsinfo_t` / `prpsinfo32_t`.
- `oprgetmap()` / `oprgetmap32()` produce old `prmap` arrays.
- `oprpdsize*()` and `oprpdread*()` implement old page-data file sizing and reads.

## Ioctl Command Flow

The main ioctl handlers follow a consistent pattern:

1. Redirect old `/proc/<pid>` directory opens to the cached PID file if `pr_pidfile` is present.
2. Reject non-process/non-LWP nodes with `ENOTTY`.
3. Require `FWRITE` for logically mutating commands, as classified by `isprwrioctl()`.
4. Reject obsolete `PIOCSXREG` with `ENOTSUP`.
5. Copy user input and decide allocation sizes before acquiring proc locks.
6. Allocate buffers before `prlock()` to avoid sleeping allocation under `p_lock`.
7. Lock the target with `prlock(pnp, zdisp)`, allowing zombies only for selected information queries.
8. Choose a target LWP via `prchoose()` unless the command operates on process-wide state or stop/wait semantics.
9. Execute the command, usually unlocking before `copyout()` or file-descriptor assignment.
10. Free any temporary allocation and assert transient `xpnp` nodes were consumed or released.

## Command Categories

Supported commands include:

- Process and u-area snapshots: `PIOCGETPR`, `PIOCGETU`.
- Stop/run control: `PIOCSTOP`, `PIOCWSTOP`, `PIOCRUN`.
- LWP discovery and file opening: `PIOCLWPIDS`, `PIOCOPENLWP`.
- Page-data opening: `PIOCOPENPD`.
- Mapped object opening: `PIOCOPENM`.
- Signal tracing and delivery: `PIOCGTRACE`, `PIOCSTRACE`, `PIOCSSIG`, `PIOCKILL`, `PIOCUNKILL`.
- Priority/nice adjustment: `PIOCNICE`.
- Syscall tracing masks: `PIOCGENTRY`, `PIOCSENTRY`, `PIOCGEXIT`, `PIOCSEXIT`.
- Legacy proc flags: `PIOCSRLC`, `PIOCRRLC`, `PIOCSFORK`, `PIOCRFORK`, `PIOCSET`, `PIOCRESET`.
- Register access: `PIOCGREG`, `PIOCSREG`, `PIOCGFPREG`, `PIOCSFPREG`, `PIOCGXREGSIZE`, `PIOCGXREG`.
- Status and ps data: `PIOCSTATUS`, `PIOCLSTATUS`, `PIOCPSINFO`, `PIOCMAXSIG`, `PIOCACTION`.
- Signal hold/fault masks: `PIOCGHOLD`, `PIOCSHOLD`, `PIOCGFAULT`, `PIOCSFAULT`, `PIOCCFAULT`.
- Credentials and groups: `PIOCCRED`, `PIOCGROUPS`.
- Usage accounting: `PIOCUSAGE`, `PIOCLUSAGE`.
- Aux vector: `PIOCNAUXV`, `PIOCAUXV`.
- x86 LDT and SPARC register-window commands behind platform conditionals.

## Locking and Concurrency

This file relies heavily on procfs locking primitives from `prsubr.c`:

- `prlock()` holds `p_lock` and marks the target process `P_PR_LOCK`.
- `prunlock()` releases that state and may force killed processes runnable.
- Address-space operations drop `p_lock` before taking `AS_LOCK_*` to avoid lock-order deadlocks.
- Register operations drop `p_lock` while touching LWP stack/register state.
- Several dynamic array commands try `KM_NOSLEEP` while locked and restart after unlock if a sleeping allocation is required.

## ABI and Compatibility Notes

The file maintains two old ABIs: native old procfs structures and 32-bit old procfs structures. The 32-bit handler rejects operations against LP64 targets when addresses, register sets, aux vectors, page data, or status structures cannot be represented. Old map/page-data formats terminate map arrays with an all-zero record.

## Dependencies

This file depends on shared procfs helpers from `prsubr.c`, including `prchoose()`, `prgethold()`, `prgetaction*()`, `prnsegs()`, `pr_iol_*()`, `break_seg()`, `pr_getsegsize()`, `pr_getprot()`, usage converters, and process locking. It also delegates actual process control to wider procfs/kernel routines such as `pr_stop()`, `pr_wait_stop()`, `pr_setrun()`, `pr_setsig()`, `pr_kill()`, `pr_setentryexit()`, `pr_setfault()`, and register accessors.

## Important Edge Cases

- `PIOCWSTOP` refuses to wait on the current process/LWP to avoid deadlock.
- System processes and `kas` address-space users are treated as having no user address space.
- `PIOCOPENM` validates mapped objects are regular vnode-backed mappings and checks read access before returning an fd.
- Page-data readers retry if `page_exists()`/`SEGOP_INCORE()`-driven nondeterminism changes the computed output size while building the buffer.
- Zone visibility is sanitized for signal info and parent PID reporting when the examiner is in a non-global zone.
