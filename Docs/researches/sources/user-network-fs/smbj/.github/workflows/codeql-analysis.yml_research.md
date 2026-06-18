# sources/user-network-fs/smbj/.github/workflows/codeql-analysis.yml

Source read signal: reviewed complete local file (70 lines, 2398 bytes).

## Purpose
`codeql-analysis.yml` covers GitHub CodeQL workflow. runs Java CodeQL analysis on pushes and pull requests to `master` plus a weekly Wednesday cron, using checkout v3, CodeQL init v2, autobuild, and analyze.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
GitHub Actions checks out full history, initializes the Java language database, lets CodeQL autobuild the Gradle project, then uploads analysis.

## State and persistence
No application state; results persist in GitHub code scanning alerts.

## Dependencies and integration points
Integrates with GitHub Actions, CodeQL, and the Java/Gradle build.

## Risks
Autobuild may miss custom integration-test or release build paths; action versions are pinned to older major versions; only Java is scanned.

## Test signals
Signals are successful workflow runs and populated CodeQL alerts on changed Java code.
