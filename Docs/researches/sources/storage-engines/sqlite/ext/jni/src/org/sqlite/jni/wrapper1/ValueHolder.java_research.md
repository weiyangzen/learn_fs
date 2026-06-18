# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ValueHolder.java

## Purpose
`ValueHolder.java` is a minimal generic mutable box used to pass values out of anonymous classes and callbacks that require captured references to be effectively final.

## Important APIs, types, and functions
- `public class ValueHolder<T>` exposes a single mutable `public T value`.
- The no-argument constructor leaves `value` null.
- The one-argument constructor initializes `value`.

## Control flow
There is no internal control flow beyond construction. Callers read and write `value` directly.

## State and persistence behavior
All state is the public field. There is no synchronization, validation, persistence, or ownership semantics.

## Dependencies and integration points
It has no non-JDK dependencies. `Tester2.java` uses it to count callback invocations, propagate result codes from `execSql()`, and hold expected hook state. Aggregate/window tests also use it as UDF state.

## Risks and edge cases
The class is intentionally mutable and unsynchronized. Sharing one holder between threads requires external synchronization or volatile/atomic alternatives if memory visibility matters.

## Test signals
Its behavior is implicitly tested wherever `Tester2` relies on callback-side mutation, especially UDF, hook, authorizer, progress, and trace tests.
