# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LiveFileMetaData.java research

## Purpose

`LiveFileMetaData` extends `SstFileMetaData` with column-family name and level information for live SST files. It is used by live-file APIs and by native interop that needs to pass a Java metadata object back into C++.

## Important APIs and types

JNI calls the private constructor with column-family bytes, level, file identity, key bounds, sequence bounds, read samples, compaction state, entry/delete counts, and checksum bytes. Public accessors are `columnFamilyName()` and `level()`. `newLiveFileMetaDataHandle()` builds a native metadata handle from the Java fields.

## Control flow

Native code creates Java instances for metadata reads. Java callers can inspect fields or request a new native handle; that call copies Java field values back over JNI.

## State and persistence behavior

The object is a point-in-time metadata copy and does not keep a live file pinned by itself. File names, key bounds, and checksums describe persistent SST state at collection time. `columnFamilyName()` returns the internal byte array, so caller mutation can affect subsequent `newLiveFileMetaDataHandle()` calls.

## Dependencies and integration points

It depends on `SstFileMetaData` and integrates with live-file APIs, backup/checkpoint tooling, and any JNI path that reconstructs native live-file metadata.

## Risks and test signals

The internal array exposure is a mutability risk. Another sharp edge is that `newLiveFileMetaDataHandle()` passes most metadata fields but not the checksum parameter visible in the constructor. Tests should verify metadata round-trips, column-family bytes, level accuracy, and handle creation with unusual key bounds.
