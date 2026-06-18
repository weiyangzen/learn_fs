# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManagerConfig.java

Purpose: Parameterized validation of snapshot RocksDB max-open-files configuration.

Important APIs and types: `OMConfigKeys.OZONE_OM_SNAPSHOT_DB_MAX_OPEN_FILES`, `OmTestManagers`, `OzoneConfiguration`, snapshot feature enablement, and JUnit parallel execution.

Control flow: for each configured value, the test creates a temp metadata dir, enables filesystem snapshots, sets all OM bind ports to dynamic values to allow concurrent execution, then either expects `OmTestManagers` construction to throw or starts and stops the managers.

State and persistence: starts a real lightweight OM test manager for valid values, writing temp metadata state. Invalid values fail before usable manager state is created.

Dependencies and integration points: integrates startup-time config validation for snapshot DB options and OM service port binding.

Risks and edge cases: only values less than `-1` are invalid; `-1`, `0`, and positive values are accepted. Parallel execution makes dynamic ports necessary to avoid flaky bind conflicts.

Test signals: `-2` throws `IllegalArgumentException`; `-1`, `0`, and `1` construct without throwing and are stopped cleanly.
