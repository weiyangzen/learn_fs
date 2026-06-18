# sources/sync-backup/kopia/tests/end_to_end_test/auto_update_test.go

## Purpose
Tests CLI auto-update check enablement, disablement, and initial delay configuration through flags and environment variables.

## Important APIs, Types, and Functions
`TestAutoUpdateEnableTest` table-drives create/connect flows. `absDuration` normalizes durations for approximate time comparison.

## Control Flow
For each case, the test creates a repository with optional flags/env, checks whether `.kopia.config.update-info.json` exists, disconnects and verifies removal, reconnects with the same options, and if enabled decodes `nextCheckTimestamp` to compare against `clock.Now()+wantInitialDelay`.

## State and Persistence Behavior
Creates and removes update-info JSON beside the client config. Environment map mutations are per test environment, and the process `KOPIA_CHECK_FOR_UPDATES` is unset before cases.

## Dependencies and Integration Points
Exercises CLI global update flags/env, repo create/connect/disconnect, config directory side effects, JSON state shape, and clock abstraction.

## Risks
Parallel cases compare wall-clock-ish times with a one-minute tolerance. The case names for flag/envar delay are slightly misleading in the source, but expected values are explicit.

## Test Signals
Confirms default enabled state, false-like env parsing, flag precedence over env, update-info cleanup on disconnect, and configured initial delay persistence.
