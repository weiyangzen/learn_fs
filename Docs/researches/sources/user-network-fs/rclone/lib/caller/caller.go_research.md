# sources/user-network-fs/rclone/lib/caller/caller.go

## Purpose
This package provides a small runtime helper for detecting whether a named function appears higher in the current call stack.

## Important APIs, types, and functions
- `Present(functionName string) bool` scans stack frames and returns true when a frame's fully qualified function name has the requested suffix.

## Control flow
`Present` collects up to 48 program counters with `runtime.Callers(3, ...)`, skipping `runtime.Callers`, `Present`, and the immediate caller. It iterates frames with `runtime.CallersFrames` and checks `strings.HasSuffix(f.Function, functionName)`.

## State and persistence behavior
The function has no persistent state. It samples the current goroutine's stack at call time.

## Dependencies and integration points
It depends on `runtime` and `strings`. Callers can use it for behavior switches that need to know whether a higher-level function is already on the call stack.

## Risks and edge cases
The suffix match can produce false positives when unrelated functions share suffixes. The fixed 48-frame buffer can miss very deep callers. It intentionally ignores the immediate caller, so direct checks for the calling function return false.

## Test signals
`caller_test.go` verifies not-found behavior, immediate-caller exclusion, and detection when wrapped in an anonymous function. Benchmarks measure shallow and 100-level stack performance.
