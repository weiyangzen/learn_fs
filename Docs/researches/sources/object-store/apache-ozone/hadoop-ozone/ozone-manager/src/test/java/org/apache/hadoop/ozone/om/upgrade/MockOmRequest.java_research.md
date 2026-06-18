# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/MockOmRequest.java

## Purpose
`MockOmRequest` is a minimal test fixture used to validate layout-version annotations on OM request classes and aspect interception of request pre-execution.

## Important APIs, Types, and Functions
- The class is annotated with `@BelongsToLayoutVersion(INITIAL_VERSION)`.
- `preExecute(OzoneManager om)` is intentionally shaped like real `OMClientRequest.preExecute` methods so `OMLayoutFeatureAspect.beforeRequestApplyTxn` can inspect the target and first argument.

## Control Flow
The method body is empty; tests do not rely on behavior inside `preExecute`. Instead, the class provides an annotation target and a method signature compatible with the aspect.

## State and Persistence Behavior
There is no state or persistence behavior. The class exists only for reflective and aspect-oriented tests.

## Dependencies and Integration Points
It depends on `OzoneManager`, `BelongsToLayoutVersion`, and `OMLayoutFeature.INITIAL_VERSION`. It integrates with `TestOMLayoutFeatureAspect`.

## Risks and Edge Cases
The fixture must remain compatible with the aspect's assumption that request `preExecute` receives `OzoneManager` as its first argument. If production request signatures change, this mock can hide or reveal aspect drift depending on whether it is updated.

## Test Signals
The class signals that request-level layout gating is annotation driven and can be tested without a full request implementation.
