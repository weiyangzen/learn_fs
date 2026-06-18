# sources/test-tools/stress-ng/stress-opcode.c

Purpose: `stress-opcode.c` implements the `opcode` stressor, generating executable pages of random, incrementing, mixed, or mutated text opcodes and forking contained children to execute them while counting attempted, successful, and signal-faulting instructions.

Important APIs/types/functions: `stress_opcode_state_t` is shared state for opcode value, attempts, successes, previous opcode, and per-signal counts. Generator methods are `stress_opcode_random()`, `stress_opcode_inc()`, `stress_opcode_mixed()`, and `stress_opcode_text()`, selected by `--opcode-method`. `stress_opcode_child_sighandler()` records signals and uses `siglongjmp` where available. A seccomp BPF filter permits only exit, signal, and `mprotect`-style syscalls and traps others.

Control flow: the parent mmaps shared state and an executable opcode arena with guard pages, chooses the method, synchronizes, and repeatedly forks. Each child installs signal handlers, marks shared state read-only, disables core dumps, drops capabilities, creates guard pages around the opcode buffer, fills the buffer, changes it to `PROT_READ | PROT_EXEC`, starts a short real-time interval timer, optionally installs seccomp, and calls into successive opcode offsets. Fault handlers either exit for termination/serious memory signals or jump back for lesser traps. The parent waits, counts a bogo op per fork, and emits metrics at shutdown.

State and persistence behavior: shared anonymous state persists across child forks during the run and is munmapped at deinit. The opcode buffer is private anonymous memory. Process signal handlers, interval timers, seccomp state, dumpability, and capabilities are child-local containment state.

Dependencies and integration points: it depends on Linux audit/filter/seccomp headers, `mprotect`, architecture opcode-size macros, cache-flush helpers, executable text address discovery, stress-ng metrics, fork retry, scheduler settings, and process naming for incrementing opcode mode.

Risks: executing arbitrary bytes is inherently crash-heavy; containment relies on guard pages, signal handling, timer aborts, seccomp, closed stdio, and child isolation. Metrics use signal counters in a page made read-only between opcode calls, so handler `mprotect()` behavior is central. Architecture opcode-size and signal semantics can make coverage and success percentages nonportable.

Test signals: direct `--opcode` plus each `--opcode-method` should produce fork/opcode/signal metrics without wedging. Important checks are no stuck child after timer expiry, no leaked executable mappings, valid unsupported-build fallback, and plausible metrics for illegal opcode, SIGBUS, SIGSEGV, SIGFPE, and SIGTRAP rates.
