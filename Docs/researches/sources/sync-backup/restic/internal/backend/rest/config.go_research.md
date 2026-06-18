<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config.go -->
# sources/sync-backup/restic/internal/backend/rest/config.go

## Purpose
Parses, masks, registers, and environment-augments REST backend configuration.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, StripPassword, prepareURL, ApplyEnvironment, and option registration are important.

## Control Flow
ParseConfig requires rest:, normalizes a trailing slash, and parses a URL. StripPassword parses the URL and replaces any password with ***. ApplyEnvironment fills username/password only when neither is present in the URL.

## State And Persistence Behavior
Config holds URL and connection count; no repository persistence.

## Dependencies And Integration Points
Depends on net/url, os, strings, internal/backend/errors/options.

## Risks And Edge Cases
Malformed URLs may be returned unchanged by StripPassword for logging safety. Environment credentials are ignored when any URL user info is already present.

## Test Signals
config_test.go covers URL normalization, unix URL syntax, and password stripping cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config.go -->
