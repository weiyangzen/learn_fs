# sources/storage-engines/rocksdb/utilities/blob_db/blob_db.cc

## Purpose
This file implements the public `BlobDB` opening helpers and option logging. It is the narrow factory layer that validates BlobDB's column-family restrictions, constructs `BlobDBImpl`, delegates initialization, and cleans up partially opened state on failure.

## Important APIs and Functions
`BlobDB::Open(const Options&, const BlobDBOptions&, const std::string&, BlobDB**)` adapts the single-`Options` convenience API into `DBOptions` plus one default `ColumnFamilyDescriptor`. On success it deletes the returned default column-family handle because `DBImpl` retains a reference to the default column family.

`BlobDB::Open(const DBOptions&, const BlobDBOptions&, const std::string&, const std::vector<ColumnFamilyDescriptor>&, std::vector<ColumnFamilyHandle*>*, BlobDB**)` is the main open path. It rejects any configuration that does not contain exactly one descriptor named `kDefaultColumnFamilyName`. It allocates a `BlobDBImpl`, calls `Open(handles)`, casts it to `BlobDB` on success, and on failure destroys any handles created by the implementation, clears the handle vector, deletes the implementation, and returns a null output pointer.

`BlobDB::BlobDB()` initializes `StackableDB` with a null wrapped DB pointer; the concrete implementation later owns the actual base DB. `BlobDBOptions::Dump()` logs all BlobDB-specific options with `ROCKS_LOG_HEADER`.

## Control Flow
Open always sets `*blob_db` to null before work begins. The convenience overload builds the default CF descriptor, delegates to the full overload, and performs default-handle cleanup only after successful open. The full overload performs validation before allocation; all post-allocation failures go through explicit cleanup to avoid leaking handles or the implementation object.

## State and Persistence Behavior
This file does not directly persist data. Its state behavior is ownership-oriented: `BlobDBImpl` is either handed to the caller as a `BlobDB*` or fully destroyed. Option dumping records effective settings for debugging, including max DB size, TTL bucket range, blob file size, GC enablement, and background-task disabling.

## Dependencies and Integration Points
The file depends on public `BlobDB` declarations, logging utilities, and `utilities/blob_db/blob_db_impl.h`. It integrates public RocksDB options and column-family descriptors with the internal `BlobDBImpl` constructor/open contract.

## Risks and Test Signals
The key behavioral restriction is no non-default column-family support. Callers passing multiple CFs or a renamed default receive `Status::NotSupported`. The most important failure-path signal is that `handles` is cleared and `*blob_db` remains null after open failure. Option dump output is the main runtime observability in this file.
