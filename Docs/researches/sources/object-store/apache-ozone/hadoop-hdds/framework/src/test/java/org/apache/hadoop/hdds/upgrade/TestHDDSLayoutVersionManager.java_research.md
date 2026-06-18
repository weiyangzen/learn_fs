<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java

Purpose: tests HDDS layout feature upgrade-action registration and monotonic layout-version numbering.

Important APIs/types/functions: `HDDSLayoutVersionManager`, `HDDSLayoutFeature`, `INITIAL_VERSION`, `DATANODE_SCHEMA_V2`, `maxLayoutVersion`, `registerUpgradeActions`, feature `scmAction`/`datanodeAction`, `HDDSUpgradeAction.execute`, and test `MockComponent` actions.

Control flow: first verifies finalized manager state does not register actions. Then a mocked unfinalized manager calls the real `registerUpgradeActions` with a test package, after which the test retrieves SCM and datanode actions from layout features, executes them against a mocked component, and verifies the correct method is invoked. The version test iterates all HDDS layout features and expects each layout version to increment by one.

State and persistence behavior: state is in-memory layout version manager metadata layout version and static feature/action registration. No disk state.

Dependencies and integration points: integrates the upgrade action annotation scan/registration mechanism with feature enum metadata and Ozone upgrade action components.

Risks: action registration depends on package scanning; missing package names or finalized-state logic can silently skip actions. Static action attachment can leak if tests are not isolated.

Test signals: asserts no actions when finalized, actions present when unfinalized, correct action classes for SCM/DN, correct execution target method calls, absent actions for non-applicable components, and strictly increasing feature versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java -->
