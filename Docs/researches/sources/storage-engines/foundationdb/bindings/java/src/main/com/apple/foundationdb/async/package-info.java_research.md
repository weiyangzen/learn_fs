<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java

## Purpose
This package descriptor documents `com.apple.foundationdb.async` as support code for asynchronous programming around Java `CompletableFuture`s in the FoundationDB binding.

## Important APIs, Types, And Functions
The file exports no runtime API; its only declaration is the package-level Javadoc and `package com.apple.foundationdb.async`. The referenced surface is `java.util.concurrent.CompletableFuture`, and the actual package contains helpers such as `AsyncUtil`, `AsyncIterable`, and `AsyncIterator` consumed by directory and test code in this group.

## Control Flow, State, And Persistence
There is no executable control flow or persistence. Its effect is documentation generation and package organization for asynchronous FoundationDB helper types.

## Dependencies And Integration Points
The directory layer relies heavily on `AsyncUtil.whileTrue`, `getAll`, `collect`, and ready futures. This descriptor gives those helpers a documented namespace in generated Java API docs.

## Risks And Test Signals
Risk is documentation drift: if async helpers change semantics, this descriptor is too generic to warn users. Test signals are indirect through compilation and generated Javadoc; no unit behavior is exercised by this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java -->
