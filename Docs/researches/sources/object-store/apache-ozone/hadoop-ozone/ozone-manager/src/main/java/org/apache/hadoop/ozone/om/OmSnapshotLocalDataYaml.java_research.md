# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalDataYaml.java

Purpose: `OmSnapshotLocalDataYaml` builds customized SnakeYAML instances for serializing and deserializing `OmSnapshotLocalData`, `VersionMeta`, and `SstFileInfo` with explicit tags and snapshot-local field names.

Important APIs and types: constants define YAML tags and `.yaml` extension. `OmSnapshotLocalDataRepresenter` tags supported classes, serializes `SstFileInfo`, `VersionMeta`, `TransactionInfo`, and UUID values, and omits null properties. `SnapshotLocalDataConstructor` registers tag constructors and type descriptions. `YamlFactory` is a Commons Pool factory that creates configured `Yaml` instances.

Control flow: serialization uses custom representers to emit stable block mappings for SST and version metadata. Deserialization constructs maps from tagged nodes, parses UUIDs and `TransactionInfo`, creates a baseline `OmSnapshotLocalData`, then overlays version, flags, timestamps, version map, and checksum. `lastDefragTime` is validated to be numeric when present.

State and persistence: no state except pooled YAML objects. It defines the on-disk YAML format for snapshot local data files and must remain compatible with checksum computation in `OmSnapshotLocalData`.

Dependencies and integration points: used by snapshot local data persistence and defrag code. Depends on SnakeYAML, Commons Pool, Ozone field-name constants, `SstFileInfo`, and `TransactionInfo`.

Risks: custom tag names and field constants form a durable file contract. Deserialization casts require YAML values to have expected types; malformed files can throw `ClassCastException`, `IllegalArgumentException`, or UUID parse errors. Changes to representer output can break checksum validation.

Test signals: cover YAML round trip with checksum, null optional fields, previous snapshot absent/present, numeric and invalid `lastDefragTime`, multiple version metadata entries, custom tag presence, pooled factory create/wrap behavior, and compatibility with older YAML missing newer optional flags.
