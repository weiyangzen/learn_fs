## sources/object-store/apache-ozone/hadoop-hdds/common/dev-support/findbugsExcludeFile.xml

**Purpose:** Defines SpotBugs/FindBugs exclusions for the `hdds-common` module.

**Important APIs/types/functions:** The XML root is `FindBugsFilter`. It excludes all bug reports for packages `org.apache.hadoop.hdds.protocol.proto`, `org.apache.hadoop.ipc_`, and `org.apache.hadoop.security_`. It also suppresses `DMI_HARDCODED_ABSOLUTE_FILENAME` specifically for class `org.apache.hadoop.ozone.OzoneConsts`.

**Control flow:** Build-time only. The SpotBugs Maven plugin reads this filter and suppresses matching findings from the analysis report.

**State and persistence:** Static build configuration persisted in source control. No runtime state.

**Dependencies and integration points:** Referenced by `hdds-common/pom.xml` through the `spotbugs-maven-plugin` `excludeFilterFile` configuration.

**Risks:** Package-level blanket exclusions can hide new static-analysis issues in generated or shaded namespaces. The `OzoneConsts` hardcoded-path suppression is narrow, but should be revisited if constants move or if real path bugs appear in that class.

**Test signals:** Build/static-analysis signal only; no JUnit coverage. Effectiveness is visible when the SpotBugs plugin runs.
