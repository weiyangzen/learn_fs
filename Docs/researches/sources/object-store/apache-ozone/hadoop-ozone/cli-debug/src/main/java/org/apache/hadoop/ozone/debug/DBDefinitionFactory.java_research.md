# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/DBDefinitionFactory.java

Purpose: `DBDefinitionFactory` maps Ozone/RocksDB paths or names to the correct `DBDefinition` used by debug DB scanners.

Important APIs and types: It uses `DBDefinition`, `SCMDBDefinition`, `OMDBDefinition`, `ReconSCMDBDefinition`, `ReconDBDefinition`, datanode schema one/two/three DB definitions, `WitnessedContainerDBDefinition`, and an `AtomicReference` for datanode schema version.

Control flow: Static initialization registers known DB names. `getDefinition(String)` normalizes OM snapshot DB names to OM DB and falls back to Recon DB prefix handling. `getDefinition(Path, ConfigurationSource)` inspects the path filename and chooses a datanode DB definition when the name ends with the container DB suffix.

State and persistence behavior: The only mutable state is the process-wide selected datanode DB schema version set by `setDnDBSchemaVersion`. No files are written.

Dependencies and integration points: It is central to `DBScanner` and `ValueSchema`, bridging CLI options such as `--dn-schema` to Ozone metadata codecs.

Risks: The schema version is global mutable state, so concurrent scans in one JVM could interfere. Unknown DB names return null and require callers to emit user-facing errors.

Test signals: Expected signals are correct DB definition resolution for OM snapshots, Recon DB prefixes, SCM/OM DBs, witnessed containers, and datanode schema-specific container DB paths.
