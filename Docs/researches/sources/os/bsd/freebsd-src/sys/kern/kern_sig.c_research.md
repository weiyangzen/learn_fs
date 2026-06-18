# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sig.c

## Purpose

Implements FreeBSD signal semantics: signal actions, masks, queues, delivery, process/thread targeting, job-control stops, ptrace stops, `SIGCHLD` reporting, invalid syscall signaling, `kqueue` signal filters, and fast userspace signal blocking.

## Main Responsibilities

- Defines signal default properties in `sigproptbl`, including terminate, core dump, stop, tty-stop, ignore, and continue behavior.
- Initializes signal queues and AST handlers in `sigqueue_start()`.
- Allocates, queues, moves, deletes, and flushes `ksiginfo_t` entries through `sigqueue_*()` helpers.
- Implements signal action syscalls:
  - `sys_sigaction()`
  - compatibility `freebsd4_sigaction()`
  - compatibility `osigaction()` and `osigvec()`
- Implements mask and wait syscalls:
  - `sys_sigprocmask()`
  - `sys_sigwait()`
  - `sys_sigtimedwait()`
  - `sys_sigwaitinfo()`
  - `sys_sigsuspend()`
  - compatibility old-mask variants
- Implements alternate signal stack handling through `sys_sigaltstack()` and `kern_sigaltstack()`.
- Implements signal send APIs:
  - `sys_kill()` / `kern_kill()`
  - `sys_pdkill()`
  - `sys_sigqueue()` / `kern_sigqueue()`
  - `pgsignal()`, `kern_psignal()`, `pksignal()`, `tdsignal()`, `tdksignal()`
- Implements delivery selection and wakeup behavior in `tdsendsignal()`, `sigtd()`, `tdsigwakeup()`, `cursig()`, `issignal()`, and `postsig()`.
- Handles ptrace signal stops and remote requests through `ptracestop()`, `ptrace_remotereq()`, `ptrace_coredumpreq()`, and `ptrace_syscallreq()`.
- Handles job-control notifications and `SIGCHLD` generation through `childproc_stopped()`, `childproc_continued()`, `childproc_exited()`, and `sigparent()`.
- Implements `nosys()` / `kern_nosys()` behavior for invalid syscalls, optionally sending `SIGSYS`.
- Implements `EVFILT_SIGNAL` attachment and event accounting.
- Manages shared `sigacts` objects and copy-on-write style signal action state.
- Implements `sigfastblock`, allowing userland to defer signal delivery with a user memory word.

## Important Control Flow

- Signal posting usually enters through `tdsendsignal()`. It selects a process or thread queue, decides whether the signal is ignored, held, caught, or defaulted, updates pending queues, schedules AST delivery, wakes sleeping threads where needed, and handles immediate stop/continue effects.
- User return signal handling uses `ast_sig()`, which repeatedly calls `cursig()` and `postsig()` while pending deliverable signals exist.
- `cursig()` delegates policy to `issignal()`, which combines thread and process pending sets, subtracts masks, handles fast-block state, and processes ignored/stopped/traced signals.
- `postsig()` removes the selected signal from queues, accepts timer signals when appropriate, either exits on default fatal action or calls the ABI-specific `sv_sendsig()` to build a user signal frame.
- Trap-generated signals use `trapsignal()`, which can immediately call `sv_sendsig()` if the signal is caught and unmasked, otherwise falls back to normal posting. If `kern.forcesigexit` is set, blocked/ignored trap signals are forced back to default handling to avoid loops.
- `kern_sigtimedwait()` temporarily unmasks the wait set, sleeps on `p_sigacts`, consumes matching queued signals, handles timer acceptance, and kills immediately on waited `SIGKILL`.

## State, Tunables, and Locking

- Signal queues exist at both process and thread level: `p_sigqueue` and `td_sigqueue`.
- Signal actions live in `struct sigacts`, protected by `ps_mtx`; process-level signal state is protected by `PROC_LOCK`.
- Pending queue allocation uses UMA zone `ksiginfo_zone`.
- Tunables include:
  - `kern.sigqueue.max_pending_per_proc`
  - `kern.sigqueue.preallocate`
  - `kern.forcesigexit`
  - `kern.lognosys`
  - `kern.signosys`
  - `kern.sigfastblock_fetch_always`
  - `kern.sig_discard_ign`
  - `debug.ptrace_attach_transparent`
- The file carefully interleaves `PROC_LOCK`, `PROC_SLOCK`, thread locks, `ps_mtx`, process group locks, and `proctree_lock`.

## Filesystem Relevance

Signals are not filesystem code, but they influence filesystem-visible behavior through process interruption and termination. `PCATCH` sleeps in VFS, buffer, mount, and driver paths depend on this signal machinery for `EINTR`/`ERESTART` behavior. `SIGKILL`, job-control stops, and ptrace stops can determine when a thread leaves or remains in filesystem code. Core dump signaling also connects to filesystem output via ABI-specific coredump hooks and ptrace-triggered coredump requests.

## Cautions

- Queueing policy distinguishes traditional bit-only pending signals from queued `ksiginfo_t`; overflow degrades some signals to simpler pending bits.
- `SIGKILL` and `SIGSTOP` have special fast paths and cannot be caught or masked.
- Stop/continue behavior is process-wide but often delivered through one selected thread.
- Ptrace can replace, discard, or requeue signals, so signal state may be deliberately re-evaluated after stops.
- Fast signal blocking depends on user memory access and can trigger `SIGSEGV` on invalid state.
