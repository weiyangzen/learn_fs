# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureUtil.java

## Purpose
`OMLayoutFeatureUtil` is a test utility for method-level layout gating. It supplies one disallowed annotated API, one basic API, and a mocked layout version manager provider for the aspect.

## Important APIs, Types, and Functions
- `ecMethod()` is annotated with `@DisallowedUntilLayoutVersion(INITIAL_VERSION)` and returns `"ec"` if allowed.
- `basicMethod()` returns `"basic"` and has no gating annotation.
- `getOmVersionManager()` returns a mocked `LayoutVersionManager` whose `isAllowed(String)` returns false first and true second, and whose `getFeature(String)` resolves to `INITIAL_VERSION`.

## Control Flow
The aspect test calls `ecMethod` through a mocked `JoinPoint`. The utility's version manager causes the first gate check to fail, producing an `OMException`. The second allowed return value supports tests that may invoke again after finalization.

## State and Persistence Behavior
No durable state exists. The only state is Mockito's ordered return behavior for the mocked version manager.

## Dependencies and Integration Points
The utility depends on layout annotations, `LayoutVersionManager`, Mockito, and `OMLayoutFeature.INITIAL_VERSION`. It integrates with `OMLayoutFeatureAspect` tests.

## Risks and Edge Cases
Because it returns a new mock manager on each call, it is not a full lifecycle simulation of layout finalization. It is intentionally narrow and should not be used as a production-like version manager.

## Test Signals
The file signals that method-level feature restrictions can be enforced independently from business logic through annotations and aspect lookup of an owning version manager.
