# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMLayoutFeatureAspect.java

## Purpose
`TestOMLayoutFeatureAspect` validates the AspectJ-based layout feature gate that blocks APIs or request pre-execution before a layout feature is finalized.

## Important APIs, Types, and Functions
- `OMLayoutFeatureAspect.checkLayoutFeature(JoinPoint)` checks method-level `@DisallowedUntilLayoutVersion`.
- `OMLayoutFeatureAspect.beforeRequestApplyTxn(JoinPoint)` checks class-level `@BelongsToLayoutVersion` on request objects.
- `OMLayoutFeatureUtil.ecMethod` and `MockOmRequest.preExecute` are fixture targets.
- `OMLayoutVersionManager.isAllowed` and `getFeature` drive allow/deny decisions.

## Control Flow
The method-level test builds a mocked join point whose target is `OMLayoutFeatureUtil` and whose method signature points to `ecMethod`. The aspect throws `OMException` containing a finalization message. The request-level test builds a mocked `OzoneManager` whose version manager denies `INITIAL_VERSION`, passes it as the first join-point argument, and asserts the same failure shape.

## State and Persistence Behavior
No persistent state is used. Temporary metadata configuration is created in setup but not materially used by the assertions. The relevant state is the mocked layout manager's denied feature status.

## Dependencies and Integration Points
The tests depend on AspectJ `JoinPoint` and `MethodSignature`, OM layout annotations, `OMException`, `OzoneManager`, and `OMLayoutVersionManager`. They protect upgrade gating at both utility-method and OM-request boundaries.

## Risks and Edge Cases
The tests assert denial paths only; allowed execution paths are mostly represented by utility behavior elsewhere. They also depend on exact annotation discovery through mocked signatures rather than woven aspect execution in a running container.

## Test Signals
The file confirms that layout gates fail closed when a feature is not finalized and that error messages explain the finalization requirement.
