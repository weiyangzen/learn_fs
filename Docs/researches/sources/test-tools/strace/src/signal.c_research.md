# sources/test-tools/strace/src/signal.c

Purpose: central signal-name, signal-mask, sigaction, signal-delivery, and realtime signal syscall decoders.

Important APIs/types/functions: `signame`, `sprintsigname`, `sprintsigmask_n`, `printsignal`, `print_sigset_addr_len`, `decode_old_sigaction`, `decode_new_sigaction`, `print_sigqueueinfo`, `do_rt_sigtimedwait`, and syscall handlers for old and rt signal APIs plus `pidfd_send_signal` and `restart_syscall`.

Control flow: helper functions map signals including realtime ranges, format dense masks by inverting them when most bits are set, and respect xlat verbosity. Old sigaction handles architecture-specific layouts and optional restorer fields; rt sigaction handles 32-bit tracees on 64-bit kernels with endian-aware mask reconstruction. Syscall handlers choose entry/exit decoding based on whether arguments are input or kernel-filled output. `rt_sigtimedwait` saves the timeout string in tcb private data on entry when siginfo will be printed on exit.

State and persistence behavior: mostly stateless, but uses static buffers for returned strings and tcb private data for `rt_sigtimedwait` timeout preservation. It reads tracee sigsets with bounded `NSIG_BYTES`, not libc `sigset_t` size.

Dependencies and integration points: depends on `nsig.h`, `signalent`, xlat tables for handlers, sigaction flags, procmask commands, pidfd flags, siginfo printers, time printers, and architecture macros (`HAVE_SA_RESTORER`, `MIPS`, `SPARC`, `ALPHA`).

Risks: signal ABI varies heavily by architecture and personality. Static string buffers are overwritten on subsequent calls. Incorrect sigset sizes can overread, so `NSIG_BYTES` and len validation are critical. Old and rt signal paths have different return-value and output-pointer semantics.

Test signals: old and rt sigaction on multiple architectures, restorer/no-restorer layouts, raw/verbose/abbrev xlat modes, dense and sparse masks, invalid sigset lengths, kill/tkill/tgkill, sigqueueinfo, pidfd_send_signal, rt_sigtimedwait entry/exit, realtime signal names, and restart_syscall output.
