# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureStateAspect.java

Purpose: `RequireSnapshotFeatureStateAspect` is an AspectJ aspect that enforces `@RequireSnapshotFeatureState` before annotated methods execute.

Important APIs and types: `checkFeatureState(JoinPoint)` is the before advice. `checkIsAllowed()` performs the policy check. Static `aspectOf()` returns a new aspect instance to avoid occasional `NoSuchMethodError` in tests.

Control flow: advice extracts the desired boolean value from the method annotation. It determines actual snapshot-feature state from one of three target shapes: `OzoneManagerRequestHandler.getOzoneManager()`, `OMClientRequest.preExecute(..)` first argument cast to `OzoneManager`, or a test-style target exposing `isFilesystemSnapshotEnabled()` by reflection. It then calls `checkIsAllowed()`. Desired `true` passes only when OM reports snapshots enabled; otherwise it throws `OMException(FEATURE_NOT_ENABLED)`. Desired `false` is not implemented and throws `NotImplementedException`.

State and persistence behavior: no state is persisted. The aspect only guards method invocation.

Dependencies and integration points: it depends on AspectJ, OM request handler/client request types, `OzoneManager.isFilesystemSnapshotEnabled()`, and `OMException`. It is part of snapshot feature compatibility and rollout gating.

Risks: unsupported join point targets throw `NotImplementedException`, so new annotation sites need aspect handling. The `preExecute` detection uses `joinPoint.toShortString().endsWith(".preExecute(..))")`, which is brittle if AspectJ string formatting changes. Desired `false` is explicitly unsupported. Missing weaving configuration would silently bypass enforcement.

Test signals: `TestRequireSnapshotFeatureStateAspect` and `SnapshotFeatureEnabledUtil` cover enabled/disabled cases and the reflection path.
