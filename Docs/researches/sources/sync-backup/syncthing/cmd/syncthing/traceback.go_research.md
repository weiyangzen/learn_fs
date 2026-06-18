# sources/sync-backup/syncthing/cmd/syncthing/traceback.go

## Purpose
This Go file adjusts Go runtime panic traceback behavior during package initialization so Syncthing panic logs include all application goroutines. It improves crash diagnostics for the monitor and crash-reporting pipeline.

## Important APIs, Types, And Functions
The only code is an `init` function calling `debug.SetTraceback("all")` from `runtime/debug`. The file is gated by `//go:build go1.7`, which is always true for modern supported Go versions but records the historical API requirement.

## Control Flow
The `init` function runs automatically before `main`. It does not branch or return errors. Once set, the runtime traceback setting affects subsequent panics and fatal runtime traces in the process.

## State And Persistence Behavior
The file changes process-global runtime debug state. It does not write files directly, but it changes the content of panic output that may later be captured by `monitor.go` into timestamped panic logs and potentially uploaded by the crash-reporting flow.

## Dependencies And Integration Points
The primary integration is with `cmd/syncthing/monitor.go`, where stderr lines beginning with panic/fatal/runtime prefixes start panic-log capture. More complete goroutine traces make those captured logs more useful. It also affects any direct process panic output outside the monitor path.

## Risks And Edge Cases
Including all goroutines can make panic logs larger and may include more contextual data from unrelated goroutines. That is usually desirable for diagnostics, but it can increase log size and privacy exposure in crash reports. Because it is an unconditional init-time process setting, tests and tools in this package inherit the same traceback behavior.

## Test Signals
There are no direct tests. Crash receiver fixtures and manual panic testing can confirm that panic logs include multiple goroutines rather than only the crashing goroutine.
