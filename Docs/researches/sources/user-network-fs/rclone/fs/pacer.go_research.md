# Research: sources/user-network-fs/rclone/fs/pacer.go

## sources/user-network-fs/rclone/fs/pacer.go

Purpose: wraps `lib/pacer.Pacer` with rclone fs configuration defaults and logging. APIs include `Pacer`, `NewPacer`, `SetCalculator`, `ModifyCalculator`, and `pacerInvoker`. `logCalculator` decorates a pacer calculator to log sleep increases and decreases.

Control flow in `NewPacer` reads low-level retry and max-connection settings from context config, creates a pacer with invoker, connection, retry, and calculator options, then wraps the calculator for logging. `SetCalculator` converts nil to the default calculator and prevents double-wrapping. `ModifyCalculator` unwraps the logging decorator while the pacer lock is held. State lives inside the embedded pacer and calculator; no persistence. Dependencies include `fserrors.RetryError` and `lib/pacer`. Integration points are backend retry loops and rate-limit handling. Risks include logging volume under frequent rate limits, reliance on context config defaults, and invalid calculator types being tolerated with log messages. Tests cover retry wrapping and no-retry call counts.
