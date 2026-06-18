# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Slow.java

Purpose: `@Slow` marks JUnit 5 tests or classes that take too much time for regular per-commit CI but may run manually or in scheduled jobs.

Important APIs and types: It targets types and methods, is retained at runtime, is meta-annotated with `@Tag("slow")`, and has optional `String value()` defaulting to empty.

Control flow: No executable code. JUnit and build tooling use the `slow` tag for test selection.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: Integrates with JUnit Jupiter tags and CI profiles that exclude or include slow tests.

Risks: Overuse can reduce coverage in normal CI. The optional value may be empty, so not every slow test has a tracking issue.

Test signals: JUnit discovery shows the `slow` tag and runtime metadata.
