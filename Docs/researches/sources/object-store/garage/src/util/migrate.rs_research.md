<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/migrate.rs -->
# sources/object-store/garage/src/util/migrate.rs

## Purpose
Versioned MessagePack migration framework for persisted Garage data structures.

## Important APIs, types, and functions
`Migrate` defines `VERSION_MARKER`, associated `Previous`, `migrate`, `decode`, and `encode`. `InitialFormat` marks root formats. `NoPrevious` terminates migration chains. Unit tests define V1/V2 to verify direct decode and migration.

## Control flow
Decode first checks the current marker and attempts rmp-serde decode. If that fails or the marker does not match, it recursively tries the previous format and maps through `migrate`. Encode prefixes the current marker and serializes as struct map.

## State and persistence behavior
This is the central persistence compatibility mechanism for files stored through `Persister`. Version markers are part of the durable disk format.

## Dependencies and integration points
Used by `Persister` and `PersisterShared`. Depends on serde and rmp-serde.

## Risks and test signals
Migration chains must remain intact for all supported upgrade paths. Empty markers on initial formats can make overly permissive decodes if formats overlap. Tests should include old bytes, new bytes, corrupted bytes, and marker preservation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/migrate.rs -->
