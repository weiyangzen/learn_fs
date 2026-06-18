<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.h -->
# sources/storage-engines/leveldb/db/builder.h

## Purpose
Declares the internal table-building helper used by LevelDB DB implementation.

## Important APIs, Types, And Functions
Forward declares `Options`, `FileMetaData`, `Env`, `Iterator`, `TableCache`, `VersionEdit`; declares `BuildTable()` returning `Status`.

## Control Flow
Header-only contract: callers pass database name, environment, options, table cache, positioned/owned iterator, and metadata structure whose number identifies the output file.

## State And Persistence Behavior
Specifies that successful non-empty builds fill the rest of `FileMetaData`; empty iterators set file size to zero and produce no table file.

## Dependencies And Integration Points
Depends only on `leveldb/status.h` plus forward declarations to keep compile dependencies small. Included by `builder.cc` and DB implementation code that needs to emit table files during flush/compaction.

## Risks
Internal API assumes caller owns object lifetimes and provides a valid `meta->number`; misuse can delete or overwrite unintended table file names.

## Test Signals
Behavior validated through `builder.cc` call sites and DB/table tests rather than direct header tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.h -->
