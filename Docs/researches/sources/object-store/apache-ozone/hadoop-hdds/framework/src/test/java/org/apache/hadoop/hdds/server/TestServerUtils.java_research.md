<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java

Purpose: comprehensive tests for `ServerUtils` filesystem/config helpers: permissions, metadata directory resolution, SCM DB directory fallback, colocated component Ratis directories, backward-compatible old Ratis paths, snapshot paths, and data-directory permission setting.

Important APIs/types/functions: `ServerUtils.getPermissions`, `getDirectoryFromConfig`, `getScmDbDir`, `getOzoneMetaDirPath`, `getRatisDirectory`, `getRatisSnapshotDirectory`, `setDataDirectoryPermissions`, config keys from `HddsConfigKeys`, `ScmConfigKeys`, `ReconConfigKeys`, `OzoneConfigKeys`, and node types `SCM`, `OM`, `DATANODE`.

Control flow: tests build temporary directory trees and `OzoneConfiguration` objects, set config keys, call resolution helpers, and assert returned files, creation side effects, exceptions, and POSIX permissions. Compatibility tests create empty/non-empty legacy `ratis` and `scm-ha` directories to verify migration/fallback precedence. Permission tests convert octal/symbolic strings to expected `PosixFilePermission` sets.

State and persistence behavior: heavily uses temp filesystem state. The helpers create metadata/database/Ratis directories, inspect legacy directory contents, and mutate POSIX permissions. Tests explicitly clean created directories in try/finally blocks where needed.

Dependencies and integration points: integrates Ozone configuration conventions, Java NIO POSIX permissions, Commons IO cleanup, node-type-specific layout rules, and legacy upgrade path compatibility.

Risks: POSIX permission tests may be platform-sensitive if run where POSIX attributes are unsupported. Backward-compatibility path selection is high risk because changing directory precedence can strand existing Ratis data.

Test signals: asserts configured/default permissions, directory creation, null/missing config behavior, rejection of multi-value metadata dirs, SCM DB fallback, mandatory metadata dir errors, distinct colocated component Ratis/snapshot dirs, old non-empty shared Ratis reuse, SCM `scm-ha` precedence, permission mutation for octal/symbolic/default values, no throw for absent directories, and read-only directory skipping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java -->
