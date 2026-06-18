# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotFeatureEnabledUtil.java

Purpose: Tiny test utility for the snapshot feature-enabled aspect. It provides a method annotated with `@RequireSnapshotFeatureState(true)` and a public feature-state accessor.

Important APIs and types: `RequireSnapshotFeatureState`, `snapshotMethod()`, and `isFilesystemSnapshotEnabled()`.

Control flow: `snapshotMethod` returns a constant string if invoked. `isFilesystemSnapshotEnabled` always returns `false`, intentionally modeling an object whose snapshot feature gate is disabled.

State and persistence behavior: No mutable state and no persistence. The utility exists to drive aspect/reflection behavior in tests outside this file.

Dependencies and integration points: The aspect under test must discover the annotation and reflectively call a public `isFilesystemSnapshotEnabled` method, mirroring `OzoneManager#isFilesystemSnapshotEnabled`. Risks are limited to method visibility/signature: changing either can break aspect tests. Test signals are indirect: aspect tests should block or allow `snapshotMethod` based on the false feature state.
