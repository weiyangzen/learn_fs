# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Flaky.java

Purpose: `@Flaky` marks JUnit 5 tests or test classes that have intermittent issues and should be handled separately by CI, often with retries.

Important APIs and types: It is an annotation targeting types and methods, retained at runtime, meta-annotated with `@Tag("flaky")`, and exposes required `String[] value()` for issue identifiers.

Control flow: There is no executable code. JUnit discovers the `flaky` tag and build tooling can include, exclude, or retry these tests based on tag selection.

State and persistence behavior: Annotation metadata is retained in compiled classes at runtime. No mutable state.

Dependencies and integration points: It integrates with JUnit Jupiter tags and project CI conventions. The value usually names Jira issues such as `HDDS-123`.

Risks: Misusing the annotation can hide real regressions from normal CI. Because `value` is required, callers must provide a tracking issue or description.

Test signals: Tagged tests are discoverable under the `flaky` JUnit tag and carry runtime annotation metadata.
