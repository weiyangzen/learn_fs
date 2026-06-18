# File Research: sources/os/bsd/openbsd-src/sys/sys/signalvar.h

Kernel-private signal action and delivery declarations.

This header defines `struct sigacts`, the per-process signal-disposition state protected by the process signal mutex and atomics. It tracks handlers, catch masks, alternate-stack signals, interrupt/restart behavior, reset-on-catch behavior, siginfo delivery, ignored signals, caught signals, and `SAS_*` flags.

It also defines internal temporary actions, pending-signal checks, default signal property bits, `sigcantmask`, `struct sigctx`, and machine-independent signal APIs such as `coredump()`, `execsigs()`, `cursig()`, `psignal()`, `trapsignal()`, `sigexit()`, and signal action allocation/init/free helpers. Machine-dependent delivery enters through `sendsig()`.

Filesystem/storage relevance: core-dump generation is filesystem-facing, and signal interruption semantics affect blocking VFS/device/socket operations. Most definitions are process-control plumbing rather than filesystem metadata.
