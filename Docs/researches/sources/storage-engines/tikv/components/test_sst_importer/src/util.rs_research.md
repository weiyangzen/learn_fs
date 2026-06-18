# Research: sources/storage-engines/tikv/components/test_sst_importer/src/util.rs

## sources/storage-engines/tikv/components/test_sst_importer/src/util.rs

Purpose: gRPC and external-storage helper module for SST importer tests. It builds upload/write request streams, invokes ingest RPCs, validates ingested raw/txn data, checks cleanup, and constructs restore-style `KvMeta` plus rewrite/range metadata.

Important APIs include `new_sst_meta`, `send_upload_sst`, `send_write_sst`, `must_ingest_sst`, `must_ingest_sst_error`, `ingest_sst`, `check_ingested_kvs(_cf)`, `check_applied_kvs_cf`, `check_ingested_txn_kvs`, `check_sst_deleted`, `make_plain_file`, `rewrite_for`, `register_range_for`, and `local_storage`. The streaming helpers send a metadata message followed by data or write batch, close the sink, and surface send/close errors if the response future fails.

State and persistence are external to the functions: importer service state, uploaded SST files, local storage directories, and in-memory buffers that are written through `ExternalStorage`. `make_plain_file` encodes key/value stream events, records the minimum start ts, length, compression marker, file name, and default CF.

Dependencies are `grpcio`, `futures`, `kvproto` import/tikv/br protobufs, `external_storage`, `tikv_util` event encoding and external IO blocking, `txn_types::Key`, `tempfile`, and `uuid`. Risks include panics on failed RPCs in `must_*`, cleanup polling with fixed 10x10 ms waits, `rewrite_for` requiring equal prefix lengths and existing prefixes, and key ordering assumptions. Test signals are direct assertions on raw get, batch get, region/import errors, and cleanup upload retry.
