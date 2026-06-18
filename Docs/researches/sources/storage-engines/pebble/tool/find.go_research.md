## sources/storage-engines/pebble/tool/find.go

Purpose: implements `pebble tool find <dir> <key>`, which finds WAL and SSTable references to a user key and range tombstones covering that key, then annotates SSTable hits with provenance from MANIFEST version edits.

Important APIs/types/functions: `findRef` records internal key, value, file number, and filename. `findT` holds command configuration and discovered manifests, WALs, tables, version edits, table metadata, blob mappings, and decode errors. `newFind` wires flags including comparer, key/value formatters, verbose mode, and `--load-blobs`. `findFiles` walks the directory, accumulates WAL logical logs, and records manifests/tables. `readManifests` decodes version edits, tracks comparer name, edit references by disk file number, and table metadata. `searchLogs` decodes batch records and matches point/range-delete entries. `searchTables` opens SSTables, applies virtual transforms from metadata, scans point and raw range-deletion iterators, and optionally loads blob values. `tableProvenance` classifies matching tables as compacted, flushed, ingested, added, and moved.

Control flow: `run` parses the key, discovers files, reads manifests, initializes blob mappings, resolves comparer/formatters, searches logs and tables, stable-sorts refs by file number/name, groups output by file, prints metadata key ranges and provenance, formats refs, then appends deferred SSTable decode errors.

State and persistence: the tool is read-only. It reconstructs in-memory history from all manifests and reads archived/current WAL and table files. Blob catalog resources are closed at the end.

Dependencies and integration: integrates VFS walking, WAL file accumulation, `record.Reader`, `pebble.Batch`, range tombstone encoding/decoding, SSTable readers/iterators, blob file mappings from sibling code, object-storage readable wrappers, and comparer-specific formatters.

Risks: explicit TODO notes virtual SST support is incomplete; disk scanning will not include purely virtual table identity, though manifest metadata helps transforms for physical hits. Provenance is approximate across manifest rollover and mixed log/ingest ordering. Corrupt WAL/SST handling favors continued output but may hide incomplete scans. Blob loading depends on catalog mappings.

Test signals: `find_test.go` routes `testdata/find` through the datadriven harness. Fixture builders create WAL, flush, ingest, compaction, tombstone, and value-separation cases.
