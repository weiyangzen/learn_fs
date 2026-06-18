## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureAspect.java

Purpose: AspectJ-based cross-cutting guard that blocks OM operations before their required layout feature is allowed.

Important APIs and types: `checkLayoutFeature` runs before methods annotated `@DisallowedUntilLayoutVersion`; `beforeRequestApplyTxn` runs before `OMClientRequest.preExecute` when the request class has `@BelongsToLayoutVersion`; `checkIsAllowed` throws `OMException(NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION)`.

Control flow: the annotation advice extracts the feature name and locates a layout version manager from known target types or reflection. The request-class advice reads the class annotation and first preExecute argument as `OzoneManager`. Both delegate to `checkIsAllowed`.

State and persistence: no persistent state. Static `aspectOf` exists to avoid intermittent test `NoSuchMethodError`.

Dependencies and integration: integrates OM request handling, `OzoneManagerRequestHandler`, `OMClientRequest`, `LayoutVersionManager`, and annotation classes.

Risks and test signals: reflection fallback to a new `OMLayoutVersionManager` can mask missing accessors by using current software layout. The pointcut only covers `preExecute`; apply-transaction paths require explicit guards elsewhere if needed. Tests should cover both annotations, failure messages, fallback behavior, current versus future layout versions, and `aspectOf`.
