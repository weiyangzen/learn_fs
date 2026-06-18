# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackEntry.java

Purpose: data holder for one stack-machine entry, preserving both the instruction index that produced the value and the value itself.

Important APIs and flow: constructor stores `idx` and `value`; fields are package-private and mutable for direct harness access. Values can be bytes, strings, numbers, tuples, futures, errors, or other objects accepted by tuple serialization helpers.

State and persistence: no persistence; entries live in `Stack` until popped or logged. Integration points are stack push/pop, `WAIT_FUTURE`, `DUP`, `LOG_STACK`, and async flattening. Risks are limited but include mutable public package state and values whose lifetime is tied to transaction futures. Test signal is preserving correct original instruction indexes in logged stack output.
