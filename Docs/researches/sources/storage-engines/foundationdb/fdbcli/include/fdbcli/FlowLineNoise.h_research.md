# sources/storage-engines/foundationdb/fdbcli/include/fdbcli/FlowLineNoise.h

## Purpose

`FlowLineNoise.h` declares `LineNoise`, a Flow-friendly wrapper around the linenoise interactive line editor. It allows fdbcli to read terminal input asynchronously while still using linenoise completion, hints, and history.

## Important APIs, Types, and Functions

- `LineNoise::Hint` holds hint text, color, bold flag, and validity.
- The `LineNoise` constructor accepts completion and hint callbacks, maximum history lines, and a multiline flag.
- `read(prompt)` returns a `Future<Optional<std::string>>`; absence means EOF.
- `historyAdd`, `historyLoad`, and `historySave` manage the linenoise history.
- `onKeyboardInterrupt()` returns a future that becomes ready on the next Ctrl-C.
- `threadPool` and `LineNoiseReader* reader` are implementation state owned by the wrapper.

## Control Flow

The header only defines the interface. `fdbcli.cpp` constructs one `LineNoise` in `runCli`, passes completion and hint lambdas, reads lines in the REPL, stores non-dangerous commands in history, and uses `onKeyboardInterrupt` in `makeInterruptable` to cancel long-running futures.

## State and Persistence Behavior

History persists to the user's `.fdbcli_history` when enabled by `runCli`. The wrapper owns thread-pool and reader objects for asynchronous integration. The comment warns that only one wrapper should exist at a time because linenoise itself supports one history, and that reads are not concurrency-safe.

## Dependencies and Integration Points

The type depends on Flow futures, `NonCopyable`, and function callbacks. Its primary integration is with fdbcli interactive mode and the platform-specific linenoise implementation compiled elsewhere.

## Risks and Edge Cases

Concurrent `read` calls or simultaneous reads with other operations are unsupported and can corrupt UI state. Because Ctrl-C is modeled as a future, callers must cancel or handle the raced operation correctly; `makeInterruptable` does this for most command futures. History persistence failures are logged by the caller, not surfaced to the user.

## Test Signals

The Python integration tests exercise `LineNoise` through subprocess interactive sessions for `kill`, `unlock`, transaction flows, and command sequences. They do not directly test completion, hints, EOF behavior, or Ctrl-C cancellation.
