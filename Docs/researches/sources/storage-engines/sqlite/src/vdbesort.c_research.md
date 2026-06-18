# sources/storage-engines/sqlite/src/vdbesort.c research

## Purpose
`vdbesort.c` implements `VdbeSorter`, the VDBE sorter for large `CREATE INDEX` and `ORDER BY` workloads. It uses an in-memory merge sort when possible and spills sorted PMAs to delete-on-close temp files when memory thresholds are exceeded. It can build incremental merge trees and use worker threads.

## Important APIs, types, and functions
Main entry points are `sqlite3VdbeSorterInit()`, `sqlite3VdbeSorterWrite()`, `sqlite3VdbeSorterRewind()`, `sqlite3VdbeSorterNext()`, `sqlite3VdbeSorterRowkey()`, `sqlite3VdbeSorterCompare()`, `sqlite3VdbeSorterReset()`, and `sqlite3VdbeSorterClose()`. Core structures include `VdbeSorter`, `SortSubtask`, `SorterRecord`, `SorterList`, `PmaReader`, `PmaWriter`, `MergeEngine`, and `IncrMerger`.

## Control flow
`Init` copies `KeyInfo`, calculates PMA thresholds from page size/cache settings, and chooses thread count. `Write` stores OP_MakeRecord blobs in memory and flushes to PMA when thresholds are crossed. Flushing sorts records and writes a PMA length followed by record-length/data pairs. `Rewind` either sorts the memory list or flushes and joins workers, then builds a merge engine or threaded incremental reader. `Next` advances memory or PMA readers. `Rowkey` returns/copies the current key, and `Compare` supports UNIQUE-index checking.

## State and persistence behavior
Sorter state is transient per VDBE cursor. It may allocate heap memory, open temp files, memory-map sorter files, spawn SQLite worker threads, and accumulates spill bytes into `db->nSpill` on close. PMA temp files are `DELETEONCLOSE` and not database-persistent.

## Dependencies and integration points
Depends on VDBE cursor/key structures, record unpack/compare logic, SQLite VFS, mmap support, worker-thread wrappers, cache/page-size configuration, database limits, and compile-time `SQLITE_MAX_WORKER_THREADS`/`SQLITE_MAX_MMAP_SIZE`. It is called by sorter opcodes and CREATE INDEX uniqueness enforcement.

## Risks and test signals
Risks include PMA offset/varint mistakes, temp-file IO errors, OOM paths, worker join ordering, incremental merge EOF handling, optimized comparator assumptions, and stable-sort differences between single-threaded and multi-threaded modes. Test small and large ORDER BY, CREATE UNIQUE INDEX duplicates/NULLs, collations/DESC, integer/text optimized paths, threshold spills, mmap on/off, worker counts, fault injection, reset/reuse, and cleanup.
