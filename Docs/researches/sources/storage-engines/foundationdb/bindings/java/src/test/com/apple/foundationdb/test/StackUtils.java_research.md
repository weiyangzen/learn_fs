# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackUtils.java

Purpose: shared conversion and error helpers for the stack-machine harness.

Important APIs and flow: `pushError` and `getErrorBytes` encode FDB errors as a tuple containing `ERROR` and the numeric code. `serializeFuture` waits on a future, maps null to `RESULT_NOT_PRESENT`, and converts FDB completion failures to error bytes. Numeric and boolean coercion helpers normalize stack operands, `createSelector` builds `KeySelector`, and `getRootFDBException` walks exception causes.

State and persistence: stateless utility class. Dependencies include `FDBException`, `KeySelector`, `Tuple`, `CompletableFuture`, and `CompletionException`. Risks include unchecked casts from generic `Object`, blocking joins in serialization, swallowing only FDB exceptions, and code-zero errors not being pushed. Signal is indirect through correctness of stack result encoding.
