# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/ContainerToKeyMapping.java

Purpose: `ContainerToKeyMapping` implements the offline `ozone debug om container-key-mapping` command. Given a comma-separated set of container IDs, it scans an OM RocksDB and emits JSON mapping each container to committed keys, optional in-progress keys, and unreferenced FSO key counts.

Important APIs and types: Public behavior is through `call`. It uses `OMDBDefinition` table definitions for volumes, buckets, directories, files, object-store keys, open files/keys, and multipart uploads. It builds a temporary `omdirtree.db` using `DBStoreBuilder`, `LongCodec`, `StringCodec`, and a `dirTreeTable`. Helper APIs include `getKeyContainers`, `prepareDirIdTree`, `reconstructFullPath`, `getDirParentNamePair`, and `jsonOutput`.

Control flow: `call` parses container IDs, opens OM DB read-only with `NO_CACHE`, initializes table handles, and delegates to `retrieve`. `retrieve` optionally builds a directory tree for full FSO path reconstruction, initializes output maps, optionally scans open file, open key, and multipart tables, then scans committed FSO file and OBS key tables. Each key's block locations are checked against target containers, paths are normalized, and Jackson writes a deterministic JSON object keyed by container ID.

State and persistence behavior: OM DB is read-only. The only write is a temporary local `omdirtree.db` next to the OM DB, deleted before and after use. Runtime state includes the volume ID cache, bucket-to-volume map, container-to-key maps, open-key maps, and unreferenced-count map. Missing FSO parent directories increment `unreferencedKeys` instead of producing a path.

Dependencies and integration points: The command is registered under `OMDebug`, consumes OM metadata table formats for both FSO and OBS buckets, and surfaces block-to-key relationships for container forensics. Tests in this group seed `OmMetadataManagerImpl` tables and execute the command through `OzoneDebug`.

Risks: The temporary DB is placed beside the inspected OM DB, so permissions and cleanup matter. `--onlyFileNames` does not affect open keys or multipart keys, which retain table-key format. FSO path reconstruction depends on directory table completeness and `name#parent` serialization. Errors during scans are printed and swallowed, yielding partial JSON.

Test signals: Existing tests cover FSO paths, OBS keys, only-file-name mode, open FSO/OBS keys, multipart uploads, missing containers, and unreferenced FSO files. Additional useful tests would cover duplicate container IDs, invalid numeric input, temporary DB cleanup on exceptions, and multiple blocks per key across containers.
