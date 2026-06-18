# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutVersionManager.java

Purpose: `HDDSLayoutVersionManager` manages HDDS layout features and registers SCM/datanode upgrade actions for storage layout finalization.

Important APIs/types/functions: constructor calls `init(layoutVersion, HDDSLayoutFeature.values())` and registers upgrade actions discovered by Reflections. `maxLayoutVersion()` returns the layout version of the last `HDDSLayoutFeature`. Visible-for-testing `registerUpgradeActions(Object... classNames)` scans supplied packages/classes. Private `registerUpgradeActions(Set<Class<?>>)` instantiates annotated `HDDSUpgradeAction` classes, reads `UpgradeActionHdds`, and attaches actions to the target feature as SCM or datanode action.

Control flow: Reflections scans configured HDDS upgrade packages (`hdds.scm.server`, `ozone.container`). Each annotated class is checked for `HDDSUpgradeAction` assignability. Actions whose feature layout version is greater than current metadata layout version are registered; finalized/older actions are skipped. Non-action annotated classes are warned.

State and persistence: inherited layout-version state comes from `AbstractLayoutVersionManager`. This class mutates `HDDSLayoutFeature` action lists in memory during construction. Persistent layout version is external metadata read by callers and passed into the constructor.

Dependencies/integration: depends on HDDS layout feature/action types, Ozone upgrade framework, `UpgradeActionHdds` annotation, Reflections classpath scanning, and SLF4J. Used by SCM and datanode startup/finalization code.

Risks: classpath scanning can miss actions if packages move or shaded/reflection behavior changes. `newInstance()` requires no-arg constructors and logs rather than failing hard on instantiation errors. Adding actions to enum feature instances can have global JVM side effects if managers are constructed repeatedly.

Test signals: `TestHDDSLayoutVersionManager` covers max layout version and action registration; SCM/datanode upgrade and finalization integration tests use this manager across layout scenarios.
