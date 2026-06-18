# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloneableException.java

## Purpose
`CloneableException` marks exceptions that can produce a new exception with a fresh backtrace at the caller site.

## Important APIs, Types, And Functions
It defines `Exception retargetClone()`.

## Control Flow
Code handling asynchronous failures can call `retargetClone` to preserve a more useful call stack when rethrowing or completing futures.

## State And Persistence Behavior
The interface stores no state. Implementations decide what error code/message/cause data is copied into the clone.

## Dependencies And Integration Points
It is part of the async package and is relevant to exception types used with asynchronous FoundationDB APIs.

## Risks And Edge Cases
Incorrect implementations may lose original error code, cause, or suppressed exceptions. The interface does not require the clone type to match exactly beyond returning `Exception`.

## Test Signals
Tests should verify cloned exceptions preserve semantic fields and have a new stack trace including the retargeting call.
