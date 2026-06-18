# sources/user-network-fs/smbj/.github/workflows/release.yml

Source read signal: reviewed complete local file (51 lines, 1365 bytes).

## Purpose
`release.yml` covers SMBJ release workflow. publishes artifacts to Sonatype when a `v*` tag is pushed, after a Java 12 `./gradlew check` gate.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
A build job checks out full history, sets up Zulu 12, chmods `gradlew`, and runs checks. The release job repeats checkout/setup and runs `clean publishToSonatype closeAndReleaseSonatypeStagingRepository` with signing and OSSRH secrets.

## State and persistence
Persistent state is external: Maven Central/Sonatype staging repositories, GitHub release permissions, and signed artifacts.

## Dependencies and integration points
Integrates GitHub Actions, Gradle publishing/signing, axion release version tags, Nexus Publish, and Sonatype credentials.

## Risks
Java 12 is dated and can diverge from CI's Java 11 coverage. A tag push can publish if secrets are present; failed staging close may need manual cleanup.

## Test signals
Signals are a passing tagged workflow, signed source/javadoc/binary jars, and a released Sonatype staging repository.
