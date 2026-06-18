<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location.go -->
# sources/sync-backup/restic/internal/backend/location/location.go

## Purpose
Parses repository location strings into scheme and config, with local-path fallback and password masking support.

## Important APIs, Types, And Functions
Location, NoPassword, Parse, StripPassword, extractScheme, and isPath are important.

## Control Flow
Parse extracts a scheme, looks it up in a Registry, and calls the factory parser; when no known scheme exists and the input looks like a path, it falls back to local: parsing. StripPassword delegates to the matched factory.

## State And Persistence Behavior
No persistence; returns parsed config objects and scheme metadata.

## Dependencies And Integration Points
Depends on strings, unicode helpers, internal/errors, and Registry/Factory from registry.go.

## Risks And Edge Cases
Ambiguous strings on Windows or with colons are sensitive; invalid schemes are rejected unless path fallback applies.

## Test Signals
location_test.go covers parse success, fallback, and invalid schemes; display_location_test.go covers masking.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location.go -->
