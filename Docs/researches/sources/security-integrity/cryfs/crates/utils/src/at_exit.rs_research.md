# sources/security-integrity/cryfs/crates/utils/src/at_exit.rs

Purpose: signal-driven exit handler that runs callbacks on termination signals and exits immediately on a quick second signal.

Important APIs/types/functions: `AtExitHandler` owns a signal thread `JoinHandle` and `signal_hook::Handle`. Global `DOUBLE_SIGNAL_HANDLER` tracks last termination signal time with a one-second threshold. `AtExitHandler::new` forces the double-signal handler and registers a user callback.

Control flow: `_new` creates `Signals::new(TERM_SIGNALS)`, spawns a named thread, logs received signals, and invokes the callback for each. `Drop` closes the signal handle and joins the thread.

State/persistence: process-global signal registrations and a background thread. No persistent files.

Dependencies/integration: uses `signal-hook`, `LazyLock`, threads, durations, instants, and logging. Integration signal tests are intentionally outside the unit-test binary.

Risks: signal tests can interfere globally, hence separation. Callback panics and `std::process::exit` behavior are TODOs. Drop can block joining the signal thread.

Test signals: local unit test only checks create/drop without signals; comments point to integration tests for real signal delivery.
