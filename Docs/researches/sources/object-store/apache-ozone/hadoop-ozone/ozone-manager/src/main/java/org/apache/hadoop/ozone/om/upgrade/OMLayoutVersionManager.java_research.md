## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutVersionManager.java

Purpose: OM-specific layout version manager that initializes feature sets, tracks metadata/software layout version, and registers OM upgrade actions.

Important APIs and types: extends `AbstractLayoutVersionManager<OMLayoutFeature>`; constructors initialize from explicit metadata layout or current software layout; `registerUpgradeActions`, `getRequestClasses`, `finalized`, and `maxLayoutVersion` are key methods.

Control flow: explicit constructor calls `init(layoutVersion)`, which initializes known features, maps initialization IO failure to `OMException(NOT_SUPPORTED_OPERATION)`, and scans the upgrade package for `@UpgradeActionOm` classes implementing `OmUpgradeAction`. Registration instantiates action classes and attaches actions only for features above current metadata layout.

State and persistence: state is inherited layout-version tracking and enum-held actions. No direct disk writes; finalization storage is handled by the upgrade finalizer/storage layer.

Dependencies and integration: uses Reflections classpath scanning over OM upgrade and request packages, `OMLayoutFeature`, `OmUpgradeAction`, and OM request classes.

Risks and test signals: `Class.newInstance` requires public no-arg constructors and hides richer construction errors in logs. Classpath scanning can be expensive or sensitive to shading. Tests should cover metadata layout greater than software layout, action registration skip/register decisions, invalid action classes, request class discovery excluding abstract classes, and `maxLayoutVersion`.
