# sources/user-network-fs/smbj/build.gradle

Source read signal: reviewed complete local file (238 lines, 6085 bytes).

## Purpose
`build.gradle` covers SMBJ Gradle build. defines a Java/Groovy library with Jacoco, license checks, Maven publishing/signing, axion-release versioning, GitHub metadata, Nexus publishing, and a `jvm-test-suite` integration-test suite under `src/it`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Default task is `build`; `check` depends on Jacoco; `release` depends on integration tests and build. Unit and integration suites use JUnit Jupiter with common dependencies, and integration tests add Testcontainers, logback, and commons-compress.

## State and persistence
Build state includes generated version from SCM tags, Gradle caches, Jacoco reports, signed Maven publications, and Sonatype staging operations.

## Dependencies and integration points
Integrates SLF4J, Bouncy Castle, MBassador, ASN.1 helpers, Mockito, AssertJ, Spock, Testcontainers, Logback, license plugin, Maven Publish, Signing, Nexus Publish, and GitHub info plugins.

## Risks
Transitive implementation dependencies are disabled globally, so missing explicit dependencies can appear at runtime. The jar manifest has a misspelled `Implenentation-Title`. Release behavior depends on tag-derived versioning and secrets.

## Test signals
Run `./gradlew check`, `./gradlew integrationTest`, `./gradlew publishToMavenLocal`, and inspect Jacoco/license output.
