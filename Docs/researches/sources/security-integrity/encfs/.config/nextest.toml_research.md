## sources/security-integrity/encfs/.config/nextest.toml

Purpose: Cargo nextest configuration. It defines slow-test handling for the default profile.

Important APIs and functions: `[profile.default]` and `slow-timeout = { period = "10s", terminate-after = 3 }`. Control flow is declarative: tests exceeding 10 seconds are marked slow and killed after three periods, i.e. about 30 seconds.

State and persistence: No runtime state beyond nextest behavior. Dependencies are `cargo nextest`, used by the Taskfile `test` task. Integration provides faster feedback and a timeout guard for unit/integration tests, while live mount tests are run separately with `cargo test`. Risk: legitimate slow cryptographic or filesystem tests may be terminated unless they are excluded or run outside nextest.
