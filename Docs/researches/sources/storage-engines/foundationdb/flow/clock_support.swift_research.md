# sources/storage-engines/foundationdb/flow/clock_support.swift

Purpose: exposes Flow network time and delay as a Swift `Clock` implementation.

Important APIs/types/functions: `FlowClock`, nested `FlowClock.Instant`, `.flow` clock extension, `now`, `minimumResolution`, `sleep(until:tolerance:)`, `sleep(for:)`, `InstantProtocol` methods, and `Swift.Duration` unit conversion helpers.

Control flow: `now` reads `flow_gNetwork_now()` and converts the `Double` seconds value into `Swift.Duration`. `sleep` computes duration to a deadline and awaits `flow_gNetwork_delay(...).value()` with `TaskPriority.DefaultDelay`.

State/persistence: `Instant` stores a `Swift.Duration` value. No persistent global state beyond Flow network state accessed through imported Flow functions.

Dependencies/integration: imports `Flow` and relies on Swift interop wrappers for Flow future `.value()`. It bridges Swift concurrency timing to Flow's event loop.

Risks: `sleep` currently ignores nanoseconds in the computed delay (`nanosDouble = 0` TODO), so sub-second precision may be wrong. Duration conversions can saturate to `.max` on overflow. Behavior depends on `gNetwork` availability.

Test signals: no local tests. Swift async code using `Task.sleep(..., clock: .flow)` is the integration signal.
