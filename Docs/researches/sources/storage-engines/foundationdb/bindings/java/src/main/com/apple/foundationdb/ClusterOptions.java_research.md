# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ClusterOptions.java

## Purpose
`ClusterOptions` is a deprecated options holder retained for the deprecated `Cluster` API. Current FoundationDB Java bindings expose no settable cluster-level options.

## Important APIs, Types, And Functions
The class extends `OptionsSet` and only exposes a constructor accepting an `OptionConsumer`. It adds no option setter methods of its own.

## Control Flow
Construction simply passes the consumer to `OptionsSet`. In `Cluster`, that consumer is a lambda that ignores all option codes and parameters.

## State And Persistence Behavior
It stores only the inherited option consumer reference. No native state is updated unless a future subclass method uses `OptionsSet.setOption`.

## Dependencies And Integration Points
It depends on `OptionsSet` and `OptionConsumer` and is reachable from `Cluster.options()`.

## Risks And Edge Cases
The class may mislead users into assuming cluster options still exist. Its behavior is intentionally inert in the current cluster wrapper.

## Test Signals
Compatibility tests should ensure `Cluster.options()` still returns a non-null `ClusterOptions` and that constructing it does not touch native state.
