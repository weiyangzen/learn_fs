# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/ContainerMapper.java

Purpose: `ContainerMapper` is a small offline fsck utility that scans an OM DB and builds a JSON mapping from container ID to local block IDs and owning key details.

Important APIs and types: Entry points are `main(String[])` and `parseOmDB(OzoneConfiguration)`. It uses `OmMetadataManagerImpl`, the default-layout key table, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OmKeyLocationInfo`, `BlockIdDetails`, and Jackson `ObjectMapper`.

Control flow: `main` reads the OM DB path from `args[0]`, sets `OZONE_OM_DB_DIRS`, calls `parseOmDB`, and prints JSON. `parseOmDB` opens metadata manager, iterates the default key table, round-trips each `OmKeyInfo` through protobuf, walks every key-location version and block location, and appends a map of local block ID to `BlockIdDetails` under each container ID.

State and persistence behavior: It is read-only. Runtime state is a nested `Map<Long, List<Map<Long, BlockIdDetails>>>`. The metadata manager is stopped in `finally`.

Dependencies and integration points: It depends on OM DB table layout for default buckets only; FSO buckets are not covered by `getBucketLayout()`.

Risks: `args[0]` is read before null/length validation. Protobuf round-trip is redundant and can throw parsing errors. The nested list-of-single-entry-maps is awkward for consumers. FSO/OBS mixed deployments may be partially mapped.

Test signals: Tests should cover missing DB config, empty key table, multiple blocks per key, multiple keys per container, default bucket-only behavior, and JSON output shape.
