# sources/user-network-fs/smbj/.github/workflows/gradle.yml

Source read signal: reviewed complete local file (51 lines, 1353 bytes).

## Purpose
`gradle.yml` covers SMBJ CI workflow. runs `./gradlew check` on Java 11 and then `./gradlew integrationTest` on Ubuntu for pushes and PRs targeting `master`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The integration job depends on the Java 11 build job, reuses Gradle cache, and relies on Docker/Testcontainers availability on `ubuntu-latest`.

## State and persistence
No runtime state except Gradle caches and CI artifacts/logs.

## Dependencies and integration points
Integrates GitHub Actions, setup-java Zulu 11, Gradle wrapper, Docker/Testcontainers, and the Gradle `check`/`integrationTest` tasks.

## Risks
Cache keys use only Gradle files, so wrapper or dependency-lock changes outside that pattern may be missed. The workflow does not chmod `gradlew`, assuming executable mode is preserved.

## Test signals
Passing Java 11 unit checks and container-backed integration tests are the main test signals.
