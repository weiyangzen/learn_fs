# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/PrefixParser.java

Purpose: `PrefixParser` implements `ozone debug om prefix`, an offline helper for inspecting FSO bucket metadata below a given prefix path in an OM DB.

Important APIs and types: It is a picocli `Callable<Void>` with required `--path`, `--bucket`, and `--volume`. Key APIs include `parse`, `dumpTableInfo`, `dumpInfo`, `getPrefixFilter`, `getParserStats`, and the `Types` enum. It uses `OmMetadataManagerImpl`, `OzoneManagerUtils.getResolvedBucketInfo`, `BucketLayout`, `KeyPrefixFilter`, and OM directory/file tables.

Control flow: `parse` validates the DB path, starts an OM metadata manager pointed at the DB directory, checks volume and bucket existence, rejects non-FSO buckets, then walks each path element by constructing OM ozone path keys from the current parent object ID. If a directory component is missing, it records a non-existent directory and dumps entries at the last valid level. It finally scans directory and file tables with a prefix filter.

State and persistence behavior: The command is read-only against OM DB. It maintains `parserStats` counters in memory and prints details to stdout, including type, effective path, DB key, object ID, and parent ID.

Dependencies and integration points: It depends on OM metadata manager table semantics for FSO object IDs and is registered under `OMDebug`.

Risks: `main` constructs `PrefixParser` without a parent, so direct invocation can dereference null unless callers use `parse` directly. `getRangeKVs` is capped at 1000 entries. Output uses `System.out` rather than command writer helpers. The path iterator and `key.getName(1)` assume a specific encoded key layout.

Test signals: Useful tests should cover invalid DB path, invalid volume, invalid bucket, OBS bucket rejection, existing nested path, missing directory, stats counters, and table-scan cap behavior.
