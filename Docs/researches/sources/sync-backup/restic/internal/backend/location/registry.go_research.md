<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/registry.go -->
# sources/sync-backup/restic/internal/backend/location/registry.go

## Purpose
Defines the backend factory registry and generic factory adapters used to construct backends from parsed config.

## Important APIs, Types, And Functions
Registry, NewRegistry, Register, Lookup, Factory, genericBackendFactory, NewHTTPBackendFactory, and NewLimitedBackendFactory are the API.

## Control Flow
Factories parse config, strip passwords, and create/open backends. HTTP factories pass RoundTripper; limited factories pass Limiter. Generic adapters convert typed config/backend constructors to interface-based Factory methods.

## State And Persistence Behavior
Registry stores factory references in a map; no repository persistence.

## Dependencies And Integration Points
Depends on context, net/http, internal/backend, and internal/backend/limiter.

## Risks And Edge Cases
Type assertions in generic factory methods will panic if callers pass a config of the wrong concrete type; location.Parse and registry usage must stay paired.

## Test Signals
Covered indirectly by config tests, location tests, and all backend factory suite tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/registry.go -->
