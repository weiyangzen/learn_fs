# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtils.java

Purpose: This suite tests additional SCM server utility behavior: datanode address fallback rules, SCM DB directory selection, stale node interval clamping, and datanode ID file path resolution.

Important APIs and types: Tests use `SCMNodeInfo.buildNodeInfo`, `ServerUtils.getScmDbDir`, `HddsServerUtil.getStaleNodeInterval`, `HddsServerUtil.getDatanodeIdFilePath`, `PathUtils.getTestDir`, `FileUtils.deleteQuietly`, and config keys for SCM datanode/client/names addresses, SCM DB directories, metadata directories, stale node interval, heartbeat interval, and datanode ID directory.

Control flow: Address tests verify explicit datanode host:port, datanode host without port, fallback to client address without honoring client port, fallback to `OZONE_SCM_NAMES` without honoring names port, and default datanode port behavior. Directory tests verify `OZONE_SCM_DB_DIRS` wins over metadata dirs and is created, metadata dirs are used as fallback and created, and missing both settings throws. Timing tests set stale node interval outside allowed bounds relative to heartbeat processing interval and expect max/min clamped values. ID-path tests verify metadata-dir fallback, empty datanode ID dir fallback, and explicit datanode ID dir selection.

State and persistence behavior: The suite creates temporary directories for SCM DB, metadata, and datanode ID path tests, then deletes them quietly. Other state is in-memory configuration.

Dependencies and integration points: These tests protect low-level configuration interpretation used during SCM and datanode startup. They complement address parsing coverage in `TestHddsServerUtil`.

Risks: Temporary directories are under a class-specific test path and must be cleaned to avoid cross-test contamination. Stale-node interval assertions encode exact clamp values derived from heartbeat processing interval and may need updates if the policy changes.

Test signals: Strong signals include correct address host/port fallback, directory creation side effects, missing-directory exception, stale interval clamp values, and datanode ID file path fallback/override behavior.
