# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRequireSnapshotFeatureStateAspect.java

## Purpose
`TestRequireSnapshotFeatureStateAspect` validates the annotation/aspect guard that blocks snapshot operations when the Ozone snapshot feature is disabled. It uses a small utility test object and mocked AspectJ join point metadata to exercise `RequireSnapshotFeatureStateAspect.checkFeatureState`.

## Important APIs, Types, and Functions
- `RequireSnapshotFeatureStateAspect.checkFeatureState(JoinPoint)` is the method under test.
- `SnapshotFeatureEnabledUtil.snapshotMethod()` supplies the annotated target method.
- AspectJ `JoinPoint` and `MethodSignature` are mocked to emulate intercepted method invocation.
- `OMException` is expected on disabled feature state.

## Control Flow
The test creates the aspect and target utility, mocks `joinPoint.getTarget()` to return the utility, mocks the method signature to resolve `snapshotMethod`, and then invokes the aspect. It asserts that the aspect throws `OMException` with the short method name included in the failure text.

## State and Persistence Behavior
No persistent state is written. The tested state is feature availability inferred by the aspect and target method metadata.

## Dependencies and Integration Points
This test integrates AspectJ-style interception with OM exception semantics. It protects CLI/RPC snapshot operations that rely on annotation-based feature gating.

## Risks and Edge Cases
- It only tests the disabled path; it does not assert the allowed path or behavior with malformed signatures.
- Message text is asserted exactly, so changes in wording require coordinated test updates.

## Test Signals
Passing means the aspect resolves the intercepted method and emits a user-facing `OMException` for disabled snapshot operations.
