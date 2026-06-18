# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/tag/Unhealthy.java

Purpose: `@Unhealthy` marks JUnit 5 tests or classes considered unstable or inconsistent to run. These tests are excluded from normal CI and run only manually or in selected jobs.

Important APIs and types: It targets types and methods, retains metadata at runtime, is meta-annotated with `@Tag("unhealthy")`, and has optional `String value()` for a Jira issue or description.

Control flow: No executable code. The annotation influences JUnit tag filtering and project CI policy.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: It integrates with JUnit Jupiter and the project's test categorization conventions.

Risks: Marking tests unhealthy can mask product regressions if not tracked and repaired. Optional empty value weakens traceability.

Test signals: Tagged tests are discoverable under the `unhealthy` JUnit tag.
