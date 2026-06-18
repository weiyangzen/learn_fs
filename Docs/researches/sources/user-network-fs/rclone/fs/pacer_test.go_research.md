# Research: sources/user-network-fs/rclone/fs/pacer_test.go

## sources/user-network-fs/rclone/fs/pacer_test.go

Purpose: validates `fs.Pacer` retry behavior. It defines `dummyPaced`, whose `fn` increments a call counter and returns a configured retry signal plus `errFoo`.

Control flow creates a pacer with short sleep bounds, invokes `Call` or `CallNoRetry`, and asserts call counts and returned error interface. `TestPacerCall` accounts for default low-level retry config, injecting a test config with 20 retries when needed. `TestPacerCallNoRetry` verifies a single invocation while still wrapping retry errors. State is test-local retry flags, counters, and optional condition variable support. Dependencies are `lib/pacer`, `fserrors.Retrier`, and context fs config. Integration signal is focused: callers can rely on retryable errors being wrapped and retry counts matching low-level retry settings. Risks not covered include calculator logging, max connection limiting, and `ModifyCalculator`.
