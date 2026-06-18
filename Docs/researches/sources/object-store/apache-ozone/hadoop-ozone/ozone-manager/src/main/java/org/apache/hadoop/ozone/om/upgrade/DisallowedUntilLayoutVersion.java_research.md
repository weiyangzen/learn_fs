## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/DisallowedUntilLayoutVersion.java

Purpose: method-level annotation used to block APIs until an OM layout feature is finalized/allowed.

Important APIs and types: runtime-retained annotation targeting `METHOD` with single value `OMLayoutFeature value()`.

Control flow and integration: enforced by `OMLayoutFeatureAspect.checkLayoutFeature` on annotated method execution. The aspect discovers a `LayoutVersionManager` from `OzoneManagerRequestHandler`, `OMClientRequest.preExecute`, a `getOmVersionManager` method, or a default manager fallback.

State, risks, and test signals: no state. Fallback to a default current-version manager can accidentally allow methods on unsupported target types. Tests should cover annotated methods on request handlers, client requests, generic classes with version manager accessors, and unsupported/fallback targets.
