# sources/storage-engines/tikv/components/engine_traits/src/file_system.rs

Purpose: Wraps filesystem IO inspection with the global TiKV IO rate limiter.

Important APIs and control flow: `FileSystemInspector` defines `read` and `write` admission methods. `EngineFileSystemInspector` stores an optional `IoRateLimiter`, can be constructed from global or explicit limiter, and delegates read/write requests with the current IO type; without a limiter it returns the requested byte count unchanged.

State, persistence, and dependencies: State is the optional shared rate limiter. No data is persisted, but returned allowances govern persistent IO behavior elsewhere.

Integration points, risks, and test signals: Used by engine filesystem adapters to apply IO throttling. Risks include missing limiter installation, wrong IO type context, partial allowance handling by callers, and treating returned length as actual IO completion. Signals are integration tests around rate limiting and backend filesystem behavior.
