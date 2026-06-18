# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ValueHolder.java

## Purpose
`ValueHolder<T>` is a tiny mutable box used where Java requires captured variables to be effectively final and where UDF aggregate state needs a mutable reference.

## Important APIs, Types, and Functions
The class exposes public field `T value`, a no-arg constructor, and `ValueHolder(T v)`.

## Control Flow
There is no behavior beyond construction and direct field access. Anonymous callback implementations mutate the boxed value to communicate with surrounding test or function code.

## State and Persistence Behavior
The holder persists exactly one mutable value. It provides no synchronization, validation, or ownership semantics.

## Dependencies and Integration Points
It is used throughout `Tester1`, SQL function implementations, aggregate/window state helpers, callback counters, and wrapper1 equivalents.

## Risks
Because `value` is public and unsynchronized, concurrent use requires external coordination. Its simplicity is intentional but easy to misuse as a shared mutable global.

## Test Signals
Indirect test signals appear in UDF accumulators, callback counters, xDestroy flags, auto-extension counters, and aggregate state checks across `Tester1` and `TesterFts5`.
