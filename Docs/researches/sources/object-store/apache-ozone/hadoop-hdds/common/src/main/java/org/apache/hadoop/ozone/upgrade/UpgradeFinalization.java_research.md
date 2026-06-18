# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalization.java

## Purpose

`UpgradeFinalization` is a client-side utility holder for Ozone upgrade finalization status, default status messages, and CLI/error handling helpers.

## APIs and control flow

Static `StatusAndMessages` constants represent starting, in-progress, required, and finalized states. The `Status` enum models finalization lifecycle states: already finalized, starting, in progress, done, and required. `StatusAndMessages` is an immutable tuple of status and message collection. `handleInvalidRequestAfterInitiatingFinalization(force, e)` suppresses `INVALID_REQUEST` only when forced; otherwise it prints guidance and throws `IOException("Exiting...")`. Helper methods classify statuses and emit standard CLI messages.

## State, dependencies, and integration

The class has only static immutable constants. It depends on `UpgradeException`, Java collections/IO, and HDDS annotations. It integrates with CLI and RPC clients monitoring upgrade finalization.

## Risks and test signals

The class writes directly to `System.out` and `System.err`, which complicates library-style reuse and tests. `isFinalized` only treats `ALREADY_FINALIZED` as finalized, while `FINALIZATION_DONE` is separate. Tests should cover forced takeover behavior, emitted messages, status predicates, and RPC translation of `StatusAndMessages`.
