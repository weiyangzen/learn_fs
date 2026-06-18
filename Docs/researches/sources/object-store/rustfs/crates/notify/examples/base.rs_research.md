# sources/object-store/rustfs/crates/notify/examples/base.rs

Purpose: shared logging helper for notify examples.

Important APIs/types/functions: `init_logger(LogLevel)` initializes a tracing subscriber with an `EnvFilter` directive and a formatted layer including target, thread names/IDs, file, and line number. `LogLevel` enum maps Debug/Info/Warn/Error to tracing filter directives.

Control flow: `main` simply initializes Info logging and logs a confirmation, but is marked dead-code because examples import the helper as a module. `init_logger` detects whether stdout is a terminal to enable ANSI coloring.

State and persistence: initializes global tracing subscriber process state once. No file persistence.

Dependencies/integration: uses `tracing_subscriber` registry/layers and `std::io::IsTerminal`. `full_demo.rs` and `full_demo_one.rs` import `init_logger` and `LogLevel`.

Risks: `.init()` panics if another global subscriber was already installed; examples are binaries so that is usually acceptable. There is a duplicated `.with_target(true)` call. `parse().unwrap()` is safe for hard-coded directives but would not be safe for arbitrary user input.

Test signals: no tests; behavior is validated by compiling/running notify examples.
