# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionConsumer.java

## Purpose
`OptionConsumer` is the internal target interface for encoded FoundationDB option setters.

## Important APIs, Types, And Functions
It defines `setOption(int code, byte[] parameter)`. Generated option wrapper classes call this through `OptionsSet`.

## Control Flow
An `OptionsSet` method encodes a typed parameter, then calls the consumer. Concrete consumers such as `FDBDatabase` and `FDBTransaction` forward codes and bytes to native JNI option setters under pointer locks.

## State And Persistence Behavior
The interface stores no state. Implementations may mutate native network, database, or transaction option state.

## Dependencies And Integration Points
It is used by `OptionsSet`, `ClusterOptions`, generated `NetworkOptions`, `DatabaseOptions`, and `TransactionOptions`.

## Risks And Edge Cases
The option code and byte parameter are untyped at this layer, so correctness depends on generated wrapper methods. Null parameters are valid for option codes with no argument.

## Test Signals
Tests should verify typed option wrappers encode into expected code/byte pairs and concrete consumers forward them to the correct native layer.
