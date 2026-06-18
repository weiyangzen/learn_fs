# sources/test-tools/stress-ng/core-log.h

## Purpose

This header defines logging flag bits and declares stress-ng logging functions.

## Important APIs, Types, And Functions

`PR_LOG_FLAGS_*` constants control error, info, debug, fail, warn, metrics, stdout/stderr, brief, lockless, skip-silent, timestamp, and syslog behavior. `PR_LOG_FLAGS_ALL` groups the normal message classes. The header declares file descriptor lookup, block locking, failure checking, YAML output, log open/close, and severity-specific printf-style logging functions.

## Control Flow

Callers use severity functions rather than writing directly. The implementation applies global filters and output routing.

## State And Persistence Behavior

The implementation uses global flags, optional log file state, shared failure state, and log locks. The header owns no state.

## Dependencies And Integration Points

It includes `core-attribute.h` for printf-format annotations and is included throughout stress-ng.

## Risks And Test Signals

Changing flag values can break option semantics. Compile checks for format annotations and runtime checks for each flag class are useful.
