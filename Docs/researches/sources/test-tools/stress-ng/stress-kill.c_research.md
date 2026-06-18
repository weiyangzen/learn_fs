# sources/test-tools/stress-ng/stress-kill.c

Purpose: implements `kill`, a signal-delivery stressor that repeatedly calls `kill()` with real, zero, broadcast-like, invalid-signal, and invalid-pid combinations.

Important APIs/types/functions: `stress_kill()` installs a `SIGUSR1` ignore handler, forks an optional child, uses `kill()` for all probes, and records a harmonic mean metric for successful measured calls.

Control flow: the parent installs signal handling, forks a child that ignores `SIGUSR1` and waits until the parent disappears or stress stops, then sync-starts. The loop gradually reduces an initial sleep delay to avoid startup starvation, measures `kill(args->pid, SIGUSR1)`, `kill(args->pid, 0)`, and `kill(-1, 0)`, exercises illegal signals and pid values, signals the child with zero, stop/continue, and `SIGUSR1`, probes a racy unused pid, and increments bogo ops. Teardown sends `SIGKILL` to the child and waits.

State and persistence behavior: state is limited to parent/child process signal state and metrics. No filesystem persistence exists.

Dependencies and integration points: uses stress-ng signal helpers, process state tracking, unused pid helper, timing, and metrics. Registered as `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, verification optional.

Risks: `kill(-1, 0)` behavior depends on permissions and process table state; verification can report failures on hardened or containerized systems. The child fork is intentionally not critical, so missing child coverage is possible under fork pressure.

Test signals: run with `--verify` under normal and containerized permissions, confirm no unexpected measured `kill` failures, child is reaped, and invalid calls do not affect process survival.
