# sources/storage-engines/foundationdb/flow/Error.cpp

## Purpose
Defines Flow error construction, name/description lookup, internal assertion error reporting, injected-fault tagging, selected retryability metadata, and a small assertion compatibility test.

## Important APIs, Types, And Functions
`Error::fromUnvalidatedCode()` sanitizes external integer codes. `Error::isDiskError()`, `Error::name()`, `Error::what()`, `Error::init()`, and `Error::asInjectedFault()` provide common error behavior. Three `internal_error_impl()` overloads print assertion context, write `InternalError` TraceEvents, include backtraces, flush traces, and return `internal_error`. `ErrorCodeTable` loads `flow/error_definitions.h`. `AttributeNotFoundError` stores a missing attribute name. `isAssertDisabled()` consults `FLOW_KNOBS->DISABLE_ASSERTS`. `transactionRetryableErrors` is a Flow-side set of retryable transaction codes.

## Control Flow
`Error` construction samples `ErrorCreated`; system error code ranges `3000..5999` produce `SystemError` TraceEvents and optionally crash if `g_crashOnError` is set. Unknown errors try to attach the current `std::exception` message. Debug logging can be compiled in through `DEBUG_ERROR`.

## State And Persistence Behavior
Global state includes `g_crashOnError`, the static error-code table, optional debug sets, and the retryable-error set. No durable state is written, but stderr, trace files, and process termination are observable side effects.

## Dependencies And Integration Points
This is core Flow infrastructure used by assertions, actor failures, network/file code, bindings-adjacent retry classification, fault injection, and unit tests. It depends on `Knobs`, `Trace`, `UnitTest`, platform backtraces, and generated error definitions.

## Risks And Edge Cases
Constructing high-severity `Error` values can recursively trace while already handling failure. `fromUnvalidatedCode()` limits arbitrary input but still accepts any value in range, relying on table lookup for names. `g_crashOnError` turns recoverable construction into process death for system-error ranges. The retryable set is duplicated with C binding logic per FIXME.

## Test Signals
`/flow/AssertTest` checks signed/unsigned comparison macro behavior. Broader signal comes from any unit or simulation test that constructs errors, triggers assertions, or validates retry handling.
