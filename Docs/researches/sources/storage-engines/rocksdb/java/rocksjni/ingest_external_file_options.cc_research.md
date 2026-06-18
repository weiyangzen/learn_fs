<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc

## Purpose
Wraps `rocksdb::IngestExternalFileOptions` for external SST ingestion.

## Important APIs and Types
IngestExternalFileOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Provides default and boolean constructor overloads, getters/setters for `move_files`, `snapshot_consistency`, `allow_global_seqno`, `allow_blocking_flush`, `ingest_behind`, and `write_global_seqno`, plus disposal.

## State and Persistence Behavior
These options directly affect persisted external-file ingestion: moving/copying files, sequence-number assignment, snapshot guarantees, flushing, and ingest-behind behavior.

## Dependencies and Integration Points
Depends on RocksDB ingestion API. Risks are combinations that can violate user expectations for snapshots or file ownership, and Java boolean constructor drift when fields are added. Tests should ingest generated SSTs across option combinations and verify sequence/snapshot behavior.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc -->
