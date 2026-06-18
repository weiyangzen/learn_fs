# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/0

Purpose: Starnix/Fuchsia reporter fixture for a Rust panic while starting an empty container. Expected title is `starnix kernel panic in src/starnix/kernel/runner/container.rs: failed to start container.: errno NUM, details: ENOENT (`.

Important parser APIs and patterns: Starnix uses `ctorFuchsia` because `NewReporter` maps `targets.Starnix` to the Fuchsia reporter. `starnixOopses` detects `STARNIX KERNEL PANIC`, extracts `info=panicked at ...` with file and message, and formats `starnix kernel panic in %[1]v: %[2]v`. `shortenStarnixPanicReport` keeps Rust stack/module lines and suppresses long unrelated runs.

Control flow: the log emits `STARNIX KERNEL PANIC`, an `ERROR` panic line at `container.rs:201:30`, an exit-without-code line, then Rust `WARN` panic/backtrace output. It includes ELF module BuildIDs, six deliberate `unrelated line` entries, and a long stack from Rust panic machinery to `Container::serve_outgoing_directory`, `main`, and libc startup. A `REPORT:` block records the expected shortened report.

State and persistence: static fixture preserving Fuchsia moniker/log prefixes, BuildIDs, Rust source paths, and async executor stack state.

Dependencies and integration: validates Starnix-specific title extraction, Rust backtrace frame regexes, BuildID module lines, unrelated-line retention limit, and shortened report generation.

Risks: log-prefix changes or too-aggressive unrelated-line filtering can drop useful backtrace context. Dynamic errno normalization must keep title dedup stable.

Test signals: expected title with `errno NUM`; expected report starts at `STARNIX KERNEL PANIC` and includes the stack through container startup.
