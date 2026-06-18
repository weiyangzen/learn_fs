<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config.go -->
# sources/sync-backup/restic/internal/backend/swift/config.go

## Purpose
Parses, registers, and environment-populates OpenStack Swift backend configuration.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, ApplyEnvironment, and option registration are key.

## Control Flow
ParseConfig accepts swift:container:/prefix syntax and requires a slash-prefixed prefix. ApplyEnvironment fills unset auth, tenant/project, application credential, storage URL/token, and default container policy fields from OpenStack/Swift environment variables.

## State And Persistence Behavior
Config stores auth credentials/tokens, container/prefix, policy, and connection count; no repository persistence.

## Dependencies And Integration Points
Depends on os, strings, internal/backend/errors/options.

## Risks And Edge Cases
Many auth modes mean precedence matters: environment values only fill empty fields. SecretString fields must avoid accidental logging.

## Test Signals
config_test.go covers parsing valid and invalid repository strings; env application is not directly covered there.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config.go -->
