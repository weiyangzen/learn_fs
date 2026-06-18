# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobInfoTest.java

## Purpose

Checks default Java wrapper values for `CompactionJobInfo`, the metadata object delivered to compaction event listeners.

## Important APIs, control flow, and dependencies

Each test creates an empty `CompactionJobInfo` and reads a single field: column family name, `Status`, thread/job ids, input/output levels, input/output file lists, table properties, compaction reason, compression type, and nested `CompactionJobStats`.

## State, persistence, risks, and test signals

No compaction is run. The state under test is the default native object. Risks are null object returns, wrong default enum values, and list/map conversion failures. Signals are empty collections, `Status.Code.Ok`, zero numeric fields, `kUnknown` reason, `NO_COMPRESSION`, and non-null stats.
