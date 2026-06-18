# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.shell` in the integration-test tree as containing test utilities for Ozone shell-related tests.

Important APIs and types: It declares the Java package and carries only package Javadoc. There are no classes, methods, fields, or annotations beyond the package declaration.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Its only integration point is Java package documentation for the shell integration-test package. The package contains large CLI integration suites such as Ozone shell, tenant shell, SCM admin, safemode, and leadership-transfer tests.

Risks: The Javadoc is generic and says "Test utils" even though the package also contains full integration tests. This is documentation-only and does not affect runtime behavior.

Test signals: None directly; package-info files are compile/documentation artifacts.
