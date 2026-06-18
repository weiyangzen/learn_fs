# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_fork.c

## Role

Implements process and LWP creation: `fork`, `vfork`, `rfork`, `lwp_create`, low-level LWP cloning, fork callbacks, process start scheduling, and process reaper control (`procctl`). It controls inheritance or sharing of vmspaces, file descriptor tables, credentials, signal actions, text vnode/namecache references, jail flags, virtual-kernel state, and scheduler/disk scheduler state.

## Major Entry Points

- `sys_fork()` calls `fork1()` with copied fd table and normal process creation flags, then starts the child and returns child pid.
- `sys_vfork()` calls `fork1()` with shared memory and parent-wait flags, starts the child, and waits for `P_PPWAIT` to clear.
- `sys_rfork()` supports creating no new process while unsharing parts of the current process, or creating a child with caller-selected sharing flags.
- `sys_lwp_create()` and `sys_lwp_create2()` create a new LWP in the current process, optionally constrained by a CPU mask.
- `fork1()` is the main process creation/unsharing routine.
- `start_forked_proc()` transitions the child from `SIDL` to runnable state and handles vfork parent synchronization.
- `sys_procctl()` implements subreaper acquisition/release/status/kill and parent-death signal controls.

## Process Creation Flow

- Validates incompatible fd flags and handles the non-`RFPROC` case by modifying the current process's vmspace and file descriptor sharing.
- Locks process group signal delivery when requested to avoid missing process-group signals during fork.
- Enforces global `maxproc` and per-uid `RLIMIT_NPROC`; increments `nprocs` before blocking allocations.
- Allocates and partially initializes `struct proc` as `SIDL`, assigns fork id, initializes token/spin/RB tree, inherits/holds the current reaper, allocates per-CPU uid accounting storage, and adds the process to allproc.
- Copies the parent process's copy region, holds credentials, sets `P_JAILED` when inherited credentials are jailed, references cached args, enters disk scheduler state, copies or shares signal actions, sets parent signal, references text vnode and copies text namecache handle.
- Handles file descriptors by creating a fresh table (`RFCFDG`), copying (`RFFDG`), or sharing with filedesc-to-leader tracking.
- Inherits limits, tty-control flags, sugid flag, virtual-kernel state, process group membership, parent/child list membership, varsym state, itimer callout, and ktrace state.
- Creates first LWP with `lwp_fork1()`, performs `vm_fork()`, wakes umtx waiters when COW may alter physical addresses, completes LWP/thread setup with `lwp_fork2()`, runs fork callbacks, sets start time and accounting flags, posts `NOTE_FORK`, and returns the child.

## LWP Creation

- `lwp_fork1()` allocates and copies the LWP copy region, initializes tokens/spin/list state, and temporarily preserves the parent's TID for fork/vfork correctness with `/dev/lpmap`.
- `lwp_fork2()` assigns vmspace, handles alt-stack inheritance/reset depending on shared memory, applies scheduler fork heuristics, allocates an LWKT thread, holds credentials for the thread, calls `cpu_fork()`, initializes per-LWP kqueue, inserts the LWP into the process RB tree with unique TID resolution, marks the process maybe-threaded, and copies blockallsigs state for lpmap when needed.
- `lwp_create1()` copies user parameters, optional CPU mask, forces exclusive limit access, creates and prepares an LWP, copies TID(s) to user memory, and schedules it.

## File-System and VFS Relevance

- Fork preserves `p_textvp` with `vref()` and copies `p_textnch`; exit and exec later release or replace these references.
- File descriptor table behavior is controlled by `RFCFDG`, `RFFDG`, or sharing; this affects open file/vnode reference inheritance.
- `vm_fork()` determines vmspace sharing or COW behavior for file-backed mappings.
- Per-LWP kqueue initialization underpins select/poll support for new threads/processes.
- Jail state is inherited through credentials and reflected in `P_JAILED`.

## Reaper Support

- `PROC_REAP_ACQUIRE` creates a subreaper owned by the caller unless already owned.
- `PROC_REAP_RELEASE` drops ownership and restores parent reaper linkage.
- `PROC_REAP_STATUS` reports owned status, refs, and head child pid.
- `PROC_REAP_KILL` walks descendants under a reaper and sends a signal without crossing subreaper boundaries unless flags restrict to direct children.
- `reaper_hold()`, `reaper_drop()`, `reaper_init()`, `reaper_exit()`, `reaper_get()`, `reaper_sigtest()`, and `reaper_kill()` manage reference-counted subreaper topology.

## Research Notes

- Error unwinding in `fork1()` relies on later labels but the fully initialized path dominates; process structures become globally visible early as `SIDL`.
- `wake_umtx_threads()` is a fork-specific COW correctness hook for user mutex waits keyed by physical address.
- The file is a key companion to `kern_exec.c` and `kern_exit.c` for tracking descriptor, vnode, namecache, vmspace, jail, and event-notification inheritance across process lifecycle boundaries.
