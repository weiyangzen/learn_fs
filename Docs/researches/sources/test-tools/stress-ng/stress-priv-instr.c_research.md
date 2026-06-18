# sources/test-tools/stress-ng/stress-priv-instr.c research

Purpose: implements `priv-instr`, a CPU stressor that repeatedly executes architecture-specific privileged instructions from user mode and verifies that they trap instead of executing silently.

Important APIs, types, and functions: `op_info_t` names each instruction, stores its function pointer, and records whether it was invalid or trapped. Architecture blocks define inline assembly operations for ARM, Alpha, HPPA, LoongArch, m68k, MIPS, OpenRISC, PPC64, RISC-V, s390, SH4, SPARC, and x86 when supported by configure probes. `stress_sigsegv_handler()` and `stress_sigill_handler()` use `siglongjmp` recovery to advance through the instruction table. x86/PPC paths optionally allocate a page for address-taking privileged instructions such as `invlpg`, `lgdt`, or `tlbie`.

Control flow: `stress_priv_instr()` resets global counters, maps an optional scratch page, installs `SIGSEGV`, `SIGILL`, and `SIGBUS` handlers, clears trap flags, synchronizes with other workers, then enters a `sigsetjmp`-protected loop. Each iteration executes the current privileged op; the signal handler records duration and trap count, marks the op, advances `idx`, and jumps back. On normal termination it reports any instructions that did not trap and records nanoseconds per trap.

State and persistence: all state is process-global and transient: `idx`, timing accumulators, trap flags, and optional anonymous page memory. No persistent files or kernel state should remain.

Dependencies and integration: depends on architecture macros, assembly helper availability, `HAVE_SIGLONGJMP`, stress-ng signal wrappers, anonymous `mmap`, and metrics. It registers as `CLASS_CPU`, `VERIFY_ALWAYS`, or an unimplemented stressor when no supported instruction set exists.

Risks: signal recovery correctness is critical; a privileged instruction that does not trap could hang or alter privileged state on broken emulation. Globals mean only one worker process should manipulate its own private copy. Handler timing includes signal overhead and is not a pure instruction latency metric.

Test signals: successful runs should record at least one trap after more than one bogo op, expose per-op unhandled instruction messages if any instruction fails to trap, and skip cleanly on unsupported architectures.
