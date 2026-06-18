<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml

## Purpose
Main unshaded Ozone filesystem module for the current Hadoop dependency line.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem`, depending on OpenTelemetry API, Hadoop common, HDDS common/config, Ozone common, Ozone filesystem common, Ratis common, and SLF4J. It disables annotation processing, builds a test jar, and lists dependencies during compile.

## Control flow
The module compiles direct filesystem classes against the main Hadoop dependency set and uses Maven jar/dependency plugins for test artifacts and dependency listing.

## State and persistence behavior
Only build outputs are created.

## Dependencies and integration points
This module provides the non-shaded full filesystem classes in `ozonefs/src/main/java`, including POSIX variants and traced Hadoop 3 APIs.

## Risks and test signals
Dependency version drift can break Hadoop API compatibility. Tests should run filesystem unit and contract suites against this artifact, especially where it differs from the shaded Hadoop 3 wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml -->
