# sources/storage-engines/lmdb/libraries/liblmdb/lmdb.h

## Purpose
Defines the public C API and documentation for LMDB: environments, transactions, databases, cursors, flags, error codes, copy/backup operations, reader management, and local encryption/checksum extension hooks.

## Important APIs, Types, And Functions
Core opaque types are `MDB_env`, `MDB_txn`, `MDB_cursor`, and database handle `MDB_dbi`. `MDB_val` carries key/data buffers. Callback types include comparison, relocation, encryption, checksum, assertion, message, string-to-key, and dynamic crypto hooks. Major APIs include `mdb_env_create/open/close/sync/copy*`, incremental dump/load, stats/info, environment sizing and flags, `mdb_txn_begin/commit/prepare/abort/reset/renew`, rollback, `mdb_dbi_open/close/drop`, comparator setters, `mdb_get/put/del`, cursor open/get/put/del/count/renew, compare helpers, reader list/check, and crypto module load/setup/unload.

## Control Flow
The documented lifecycle is create environment, configure mapsize/readers/maxdbs/page size/encryption/checksum as needed, open the environment, begin transactions, open DB handles, perform get/put/delete or cursor operations, commit or abort, then close cursors, DB handles when necessary, and finally the environment. Backup/copy APIs internally use read transactions. Two-phase support splits commit into prepare plus commit and allows constrained rollback of the last committed transaction.

## State And Persistence Behavior
LMDB exposes a memory-mapped copy-on-write B-tree with ACID transactions. Read transactions view stable snapshots and can keep freed pages from being reused; write transactions are serialized. Environment flags tune durability (`MDB_NOSYNC`, `MDB_NOMETASYNC`, `MDB_MAPASYNC`), mapping mode (`MDB_WRITEMAP`, `MDB_FIXEDMAP`, `MDB_REMAP_CHUNKS`), locking (`MDB_NOTLS`, `MDB_NOLOCK`), layout (`MDB_NOSUBDIR`), and read-only behavior. Database contents, metadata pages, reader tables, lock files, mapsize, and optional encryption/checksum state are the persistent integration surfaces.

## Dependencies And Integration Points
The header depends on system types, integer formatting macros, and platform file-handle abstractions. It is consumed by `mdb.c`, command-line tools, tests, language bindings, and loadable crypto modules such as `crypto.c`. The makefile installs it as the public include file.

## Risks And Edge Cases
The comments document several operational hazards: stale readers grow the DB, long-lived write transactions block writers, fork reuse is unsafe, opening the same DB twice in one process can break advisory locking, remote filesystems are unsupported, read-only mode still usually writes lock files, and `MDB_NOLOCK` shifts all concurrency correctness to the caller. Pointer values returned in `MDB_val` are transaction-scoped and must not be modified. Comparator changes after data access can corrupt ordering. Durability flags deliberately trade crash safety for speed.

## Test Signals
Header-level signals come from compiling all LMDB tools/tests and external consumers. Runtime signals include transaction commit/abort behavior, cursor traversal modes, duplicate sorting, map resize handling, stale reader cleanup, copy/compact/incremental backup flows, encryption/checksum hook failures, and correct error-code propagation.
