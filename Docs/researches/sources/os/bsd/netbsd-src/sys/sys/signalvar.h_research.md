# File Research: sources/os/bsd/netbsd-src/sys/sys/signalvar.h

Read completely: 325 lines.

This kernel signal-internals header defines queued signal lists, shared signal actions, pending-signal state, process signal context, internal action properties, and machine-independent signal APIs. `struct sigacts` contains per-signal `struct sigaction`, trampoline pointer, and version, plus refcount and lock. `sigpend_t` combines a `ksiginfo` queue with a signal set, and `struct sigctx` stores debugger/core-dump signal state and catch/ignore/pass masks.

It declares signal delivery, coredump, process group signaling, trap signaling, signal action/mask/suspend/altstack helpers, pending queue operations, ksiginfo allocation/free, sigtimedwait support, notification helpers, and machine-dependent `sendsig_*` functions. Inline helpers find the first signal in a set and manage ksiginfo queues.

With `SIGPROP`, it defines the default action/property table for all signals; otherwise it declares `sigprop`.

Risks: signal actions can be shared between processes and must be unshared before mutation. Queue flags and pending sets must remain consistent or delivery, masking, and debugger behavior diverge.
