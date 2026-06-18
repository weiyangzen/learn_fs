# sources/distributed-fs/xrootd/src/XrdCl/XrdClFinalOperation.hh

## Purpose
`XrdClFinalOperation.hh` declares a small pipeline finalizer type. It lets operation pipelines register a callback that is always executed regardless of prior pipeline success or failure, typically for cleanup or resource management.

## Important APIs, Types, And Functions
`FinalOperation` stores `std::function<void(const XRootDStatus&)> final`. Its constructor accepts the function by value and moves it into storage. `ConcreteOperation` is a friend template, allowing pipeline internals to access and invoke the private function. `typedef FinalOperation Final` provides a shorter user-facing name.

## Control Flow
The header does not execute the callback itself. Pipeline implementation in `ConcreteOperation` is expected to detect this final operation and call `final(status)` with the terminal pipeline status.

## State And Persistence Behavior
The only state is the in-memory function object. It may capture external resources, so lifetime is determined by pipeline ownership of the `FinalOperation`.

## Dependencies And Integration Points
It depends on `<functional>` and the forward-declared `XRootDStatus`. It is part of the operation composition system used by file and filesystem operation headers.

## Risks And Test Signals
Tests should prove final callbacks run on both success and failure, receive the correct status, and run exactly once. Capturing resources by reference is a user risk; pipeline docs and examples should prefer ownership-safe captures.
