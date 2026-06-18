# Research: sources/storage-engines/tikv/components/test_sst_importer/src/lib.rs

## sources/storage-engines/tikv/components/test_sst_importer/src/lib.rs

Purpose: provides Rocks-backed SST test fixtures and metadata helpers. It exports `TestEngine`, `RocksSstWriter`, all utilities from `util`, and `PROP_TEST_MARKER_CF_NAME`, a table property marker recording the CF used to create an SST.

Important APIs create test Rocks engines with CF options and optional env, SST readers/writers, CRC32 checksums, DB range assertions, and several SST generators: by numeric range, raw TiDB key/value pairs, plain key/value pairs, or an existing DB. `read_sst_file` reads bytes, computes CRC32, assigns a UUID, fills key range/length/CF name, and returns `(SstMeta, data)`. `TestPropertiesCollectorFactory` injects marker properties into SST table properties.

Control flow is synchronous: build Rocks options, attach the property collector, create DB/SST writer, encode keys through `keys::data_key` or `txn_types::Key`, finish SST, then compute metadata from file bytes. Persistence is explicit on the supplied paths: Rocks DB directories and SST files remain until the test temp dirs are dropped.

Dependencies include `engine_rocks` raw table property APIs, `engine_traits` writer traits, `kvproto::import_sstpb`, `uuid`, `keys`, and `txn_types`. Risks include assuming input KVs are non-empty and sorted enough for SST writing, defaulting CF name to `"default"` in metadata, and panics on file/engine errors. Test signals are range checks and downstream importer tests validating CRC, length, range, CF marker properties, and ingest behavior.
