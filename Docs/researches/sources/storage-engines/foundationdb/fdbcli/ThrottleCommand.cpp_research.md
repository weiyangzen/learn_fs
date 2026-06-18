# sources/storage-engines/foundationdb/fdbcli/ThrottleCommand.cpp

## Purpose

`ThrottleCommand.cpp` implements the `fdbcli throttle` command family for viewing and controlling transaction tag throttles. It covers manual tag throttling, unthrottling by filter, automatic throttling enablement, list output, completion suggestions, and inline command hints. The implementation is intentionally thin over `ThrottleApi`, so the file's main local responsibilities are CLI grammar, argument validation, human-readable output, and registering command metadata.

## Important APIs, Types, and Functions

- `throttleCommandActor(Reference<IDatabase>, std::vector<StringRef>)` is the command actor. It handles `list`, `on tag`, `off`, `enable auto`, and `disable auto`.
- `ThrottleApi::getThrottledTags`, `getRecommendedTags`, `throttleTags`, `unthrottleTags`, `unthrottleAll`, and `enableAuto` provide the persistent system-key operations.
- `TagThrottleInfo`, `TagSet`, `TagThrottleType`, `TagThrottledReason`, and `TransactionPriority` are the key domain types.
- `parseDuration`, `transactionPriorityToString`, `tokencmp`, `printUsage`, and `printable` are shared CLI helpers.
- `throttleGenerator` and `throttleHintGenerator` provide shell completion and progressive hints.
- The static `CommandFactory throttleFactory` publishes the public help text and registers the command name.

## Control Flow

The actor first rejects a bare `throttle` by printing usage. `list` validates an optional mode (`throttled`, `recommended`, or `all`) and optional integer limit, fetches matching records through `ThrottleApi`, then prints only unexpired entries. `on tag <TAG>` parses optional TPS rate, duration, and priority, validates nonnegative rate and nonzero duration, builds a single-tag `TagSet`, and persists a manual throttle. `off` scans a flexible set of filters: throttle type, priority, and optional `tag <TAG>`. If no tag is supplied it calls `unthrottleAll`; otherwise it calls `unthrottleTags`. `enable auto` and `disable auto` validate the fixed grammar and toggle the automatic throttling flag.

## State and Persistence Behavior

This command persists all changes through `ThrottleApi`, which writes FoundationDB system metadata for throttled tags and auto-throttling enablement. `throttle list` reads current throttle metadata and filters against `now()` so expired throttles do not appear in the table. Manual throttles are written with `TagThrottleType::MANUAL`; `off all` clears both manual and auto throttles by passing an empty `Optional<TagThrottleType>`.

## Dependencies and Integration Points

The file integrates with `fdbcli.h` command registration, `IClientApi` database handles, tag throttle system data, transaction priority formatting, Flow coroutines, and CLI completion infrastructure. It is dispatched from `fdbcli.cpp` when the first token is `throttle`.

## Risks and Edge Cases

The `list` limit parser accepts `strtol` output without checking negative values or overflow. A negative limit would be passed to `ThrottleApi` and may have surprising behavior depending on downstream validation. The parser uses `tokens.size()` in some checks that are redundant after earlier validation but harmless. Output is exact-text sensitive because integration tests compare CLI strings. Another subtlety is that `list all` can print "There are no throttled tags" even when only recommended tags were requested by a different branch; the wording is selected from `reportThrottled`.

## Test Signals

`fdbcli_tests.py` contains a disabled `throttle()` integration test that checks empty list output and verifies `throttle enable auto` / `disable auto` by reading the system key `\xff\x02/throttledTags/autoThrottlingEnabled`. Useful additional coverage would exercise manual `on tag`, duration parsing, priority-specific unthrottle, `list all`, invalid limit, negative rate, and completion hints.
