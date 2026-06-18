# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutFeature.java

## Purpose
Enumerates HDDS layout features and versions used by upgrade/finalization logic.

## Important APIs and types
Enum values define layout versions from `INITIAL_VERSION` through `STORAGE_SPACE_DISTRIBUTION`. It implements Ozone `LayoutFeature`, exposing `layoutVersion()` and `description()`. Optional SCM and datanode upgrade actions can be registered with `addScmAction` and `addDatanodeAction`, and retrieved with `scmAction()`/`datanodeAction()`.

## Control flow and state
Each enum value stores layout version, description, and at most one SCM and datanode action. Add methods only set the action when the current field is null, preserving first registration.

## Dependencies and integration points
Used by HDDS upgrade framework, datanode/SCM layout version managers, and `BelongsToHDDSLayoutVersion` annotations.

## Risks and test signals
Tests should assert monotonic layout version ordering, descriptions, action first-wins behavior, and optional absence/presence. Enum fields are mutable, so parallel tests registering actions must avoid cross-test contamination.
