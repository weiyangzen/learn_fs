# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizer.java

## Purpose

`UpgradeFinalizer<T>` defines the service-facing API for finalizing metadata upgrades and reporting progress. The complete 99-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `finalize`, `finalizeAndWaitForCompletion`, `reportStatus`, and `getStatus`. It also defines a shared SLF4J `LOG`.

## Control Flow

The interface defines the expected flow: initiate finalization for a client ID and service context, optionally wait for completion, poll status messages, and read current status.

## State and Persistence Behavior

Implementations coordinate in-memory upgrade state and persistent layout version updates through `LayoutFeature` actions and storage VERSION files.

## Dependencies and Integration Points

It depends on `UpgradeFinalization.Status`, `StatusAndMessages`, `LayoutFeature.UpgradeAction`, and Ozone stability annotations. `BasicUpgradeFinalizer` is the base implementation.

## Risks and Edge Cases

Client ID ownership and takeover semantics are implementation-dependent. Finalization can be background-driven, so callers must poll and handle partial progress/failures.

## Test Signals

Contract tests should cover initiation, polling, takeover, wait timeout/success, and status consistency across service-specific finalizers.
