# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureStrings.java

## Purpose
`FutureStrings` adapts native futures returning string arrays, used for storage server address locality information.

## Important APIs, Types, And Functions
The class extends `NativeFuture<String[]>`, registers the marshal callback, and calls native `FutureStrings_get`.

## Control Flow
`FDBTransaction.getAddressesForKey` creates it. Native readiness triggers string array extraction and Java future completion through the base class.

## State And Persistence Behavior
Only the inherited pointer is mutable before completion; completed string arrays live on the Java heap.

## Dependencies And Integration Points
It integrates with `LocalityUtil.getAddressesForKey` through `FDBTransaction`.

## Risks And Edge Cases
Locality information can be unavailable and complete exceptionally. Address format depends on transaction options such as include-port.

## Test Signals
Tests should cover successful address arrays, unavailable-locality errors, cancellation, and executor callback behavior.
