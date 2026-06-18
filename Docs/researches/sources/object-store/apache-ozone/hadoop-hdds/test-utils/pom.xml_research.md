# sources/object-store/apache-ozone/hadoop-hdds/test-utils/pom.xml

Purpose: This Maven module descriptor builds the shared `hdds-test-utils` jar used by Ozone and HDDS tests. It centralizes test helper dependencies and disables annotation processing for this utility module.

Important APIs and types: The POM inherits from `org.apache.ozone:hdds`, sets artifact `hdds-test-utils`, packaging `jar`, and version `2.3.0-SNAPSHOT`. Dependencies include reload4j, Guava, commons-io/lang3, Jakarta annotations, Log4j API/core, Ratis common, AssertJ, JUnit Jupiter API, Mockito, SLF4J, Hadoop common as provided with all transitive dependencies excluded, JaCoCo core as provided, and JUnit platform engine/launcher as provided.

Control flow: Maven resolves the parent and dependencies, compiles utility classes, and uses `maven-compiler-plugin` with `<proc>none</proc>` to prevent annotation processing.

State and persistence behavior: Build metadata only. It affects generated artifacts in the Maven target directory, not runtime application persistence.

Dependencies and integration points: This module provides helper classes imported throughout the source tree, including wait utilities, log capturers, metrics assertions, test clocks, tag annotations, and timeout listeners. Its dependency scopes avoid pulling some heavy runtime dependencies into consumers.

Risks: Excluding all transitive dependencies from Hadoop common requires required classes to be supplied elsewhere. Provided dependencies must be available in test runtime or build plugins. Dependency drift can break helpers that bridge Log4j1, Log4j2, and SLF4J.

Test signals: Successful Maven compile/test classpath resolution for downstream modules that depend on `hdds-test-utils`.
