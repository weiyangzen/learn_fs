# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RequireSnapshotFeatureState.java

Purpose: `RequireSnapshotFeatureState` is a runtime method annotation used to require a desired filesystem snapshot feature state before invoking annotated operations.

Important APIs and types: it targets methods, is retained at runtime, and has one boolean element `value()`. Current production use is for `true`, meaning snapshot feature must be enabled.

Control flow and state: the annotation itself has no behavior. `RequireSnapshotFeatureStateAspect` provides the runtime enforcement through AspectJ before advice.

Dependencies and integration points: it integrates with methods on OM request handlers, OM client requests, and test utility classes that need snapshot feature gating.

Risks: annotated methods are protected only when AspectJ weaving/configuration includes the aspect. The aspect's comments note that classes may need to be added to `META-INF/aop.xml` if the annotation does not take effect.

Test signals: `SnapshotFeatureEnabledUtil` and `TestRequireSnapshotFeatureStateAspect` cover enforcement paths.
