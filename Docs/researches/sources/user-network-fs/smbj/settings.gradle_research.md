# sources/user-network-fs/smbj/settings.gradle

Source read signal: reviewed complete local file (1 lines, 26 bytes).

## Purpose
`settings.gradle` covers Gradle settings. sets the root project name to `smbj`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Gradle reads it before project evaluation to name publications, tasks, and build scans.

## State and persistence
No runtime state.

## Dependencies and integration points
Integrates with Gradle project identity and build.gradle's publication metadata.

## Risks
Changing the name affects artifact/module naming and automatic module name composition.

## Test signals
Run `./gradlew projects` or inspect publication coordinates.
