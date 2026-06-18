<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/pom.xml

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/pom.xml_research.md`.

## Purpose
Maven module descriptor for `ozone-fault-injection-test`, declaring build plugins and dependencies used by this Ozone submodule. The file has 108 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Artifact/dependency declarations include `ozone-fault-injection-test, ozone-network-tests, maven-compiler-plugin, maven-resources-plugin, exec-maven-plugin`. Build plugins detected: `exec-maven-plugin, maven-compiler-plugin, maven-resources-plugin`.

## Control Flow
Maven consumes this descriptor during reactor builds to resolve module dependencies, generate resources/classes, apply static-analysis exclusions, and bind configured plugin executions.

## State And Persistence Behavior
The descriptor has no runtime state but controls build outputs under Maven `target/`, generated sources/resources, dependency resolution, and plugin reports.

## Dependencies And Integration Points
Maven artifacts `ozone-fault-injection-test`, `ozone-network-tests`, `maven-compiler-plugin`, `maven-resources-plugin`, `exec-maven-plugin`; tools `docker`, `pytest`; configuration keys `Apache Ozone Network Tests`.

## Risks And Edge Cases
- Dependency/plugin drift can affect generated sources, static-analysis scope, and module packaging.
- Skipping or excluding transitive dependencies can surface only at runtime or integration-test time.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/pom.xml -->
