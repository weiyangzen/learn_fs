# Agent 05 Candidate: Storage Engines Relevant to Filesystem Design

Date: 2026-06-15

Scope: database, LSM, log-structured, page-manager, object-backed, and replicated-log storage engines whose source code directly helps study filesystems or distributed filesystems. This is a source-only research subset, not a buildable vendor tree.

## Position in `learn_fs`

This candidate should live under `engines/` and complement kernel/filesystem/object-store candidates from other agents. It should not be expected to satisfy the repository-wide 20M-200M LOC target by itself. The verified core subset here is roughly a few thousand source files, likely below 1M LOC after tests and generated artifacts are excluded. Expanding it by vendoring complete dependency graphs would weaken the "only source directly useful for filesystem design" rule.

Recommended directory layout:

```text
learn_fs/
  engines/
    lsm/
      leveldb/
      rocksdb/
      badger/
      pebble/
    btree/
      wiredtiger/
    page/
      sqlite/
    distributed/
      foundationdb/
      tikv/
      raft-engine/
```

The machine-readable selection list is in `agent05-storage-engines.yaml`.

## Selection Rules

Include source that teaches one of these filesystem-adjacent mechanisms:

- WAL, journal, manifest, record, raft log, or log file format.
- SST/table/block/page layout, B-tree page manager, page cache, block cache, eviction, and checksums.
- LSM write path, memtable, flush, compaction, range deletion, tombstone handling, blob/value separation, and garbage collection.
- VFS/env/file abstraction, direct I/O, fsync, file locking, rate limiting, async I/O, and pluggable filesystem backends.
- Snapshots, checkpoints, backup/restore, crash recovery, rollback-to-stable, and corruption handling.
- Object or remote storage backends, tiered/disaggregated storage, shared cache, and remote object catalogs.
- Distributed storage server, replicated log, shard/region movement, split/merge, snapshot transfer, and recovery.

Exclude by default:

- Language bindings, package metadata, CI, website/docs, generated release assets, broad SQL/query layers, CLIs, benchmark harnesses, fuzzers, and large test suites.
- Tests are excluded from the primary source mirror, but a later "oracle" pass may selectively add crash-consistency or format-compatibility tests.

## Candidate Inventory

### `engines/lsm/leveldb`

Upstream: `https://github.com/google/leveldb.git`

Verified branch/commit: `main` at `7ee830d`

Include:

- `db/`
- `table/`
- `util/`
- `helpers/memenv/`
- `include/leveldb/`
- `port/`
- `doc/log_format.md`

Why it matters:

- Small, readable reference LSM with WAL, memtable, table cache, SST block format, version edits, version set, and Env abstraction.
- Best first read before RocksDB and Pebble because the design is compact enough to trace end to end.

Exclude:

- `benchmarks/`, `issues/`, `third_party/`, most tests.

Risk:

- Too small for modern production features such as blob files, remote object storage, advanced compaction, and distributed snapshots. That is intentional; use it as the baseline, not the endpoint.

### `engines/lsm/rocksdb`

Upstream: `https://github.com/facebook/rocksdb.git`

Verified branch/commit: `main` at `c9252b9`

Include:

- `db/`, especially `db/blob/`, `db/compaction/`, `db/db_impl/`
- `table/`, especially `table/block_based/`
- `memtable/`
- `file/`
- `env/`
- `cache/`
- `utilities/transactions/`
- `utilities/checkpoint/`
- `utilities/backup/`
- `utilities/blob_db/`
- `utilities/persistent_cache/`
- `utilities/sorted_run_builder/`
- `utilities/table_properties_collectors/`
- `utilities/write_batch_with_index/`
- `include/rocksdb/`
- `util/`, `options/`, `monitoring/`, `memory/`, `logging/`, `port/`

Why it matters:

- Production LSM write path, WAL, MANIFEST/versioning, flush, compaction scheduling, table formats, file deletion, range deletes, snapshots, transactions, checkpoints, backup, blob files, and persistent cache.
- `env/` and `file/` are especially valuable for studying filesystem contract assumptions: writable files, random-access files, sequential files, fsync, direct I/O, mmap, rate-limited I/O, and custom backends.

Exclude:

- `java/`, `third-party/`, `db_stress_tool/`, `microbench/`, `fuzz/`, `coverage/`, `wiki/`, most tests.

Risk:

- RocksDB is broad; including all utilities can dilute the research set. Keep the initial mirror to paths listed above and add utilities only when they teach file lifecycle, durability, or storage layout.

### `engines/lsm/badger`

Upstream: `https://github.com/dgraph-io/badger.git`

Verified branch/commit: `main` at `284cea0`

Include:

- Top-level `*.go` core files such as `db.go`, `txn.go`, `memtable.go`, `levels.go`, `level_handler.go`, `compaction.go`, `manifest.go`, `value.go`, `discard.go`, `stream.go`, `backup.go`
- `table/`
- `skl/`
- `y/`
- `options/`
- `fb/BlockOffset.go`
- `fb/TableIndex.go`

Why it matters:

- Clear implementation of value-log separation: hot LSM metadata plus append-heavy value log, discard statistics, and value GC.
- Direct analogy to log-structured filesystems: segment cleaning, large object separation, space amplification, and read amplification tradeoffs.

Exclude:

- `badger/cmd/`, `integration/`, `images/`, `docs/`, `trie/`, `pb/`, tests.

Risk:

- Generated protobuf/flatbuffer code is mostly format plumbing. Keep generated index structs only if needed to follow SST index layout.

### `engines/lsm/pebble`

Upstream: `https://github.com/cockroachdb/pebble.git`

Verified branch/commit: `master` at `b658835`

Include:

- Top-level `*.go` core files
- `internal/arenaskl/`
- `internal/base/`
- `internal/cache/`
- `internal/compact/`
- `internal/manifest/`
- `internal/rangedel/`
- `internal/rangekey/`
- `internal/sstableinternal/`
- `internal/keyspan/`
- `objstorage/`
- `record/`
- `sstable/`
- `vfs/`
- `wal/`
- `batchrepr/`
- `valsep/`
- `rangedel/`
- `rangekey/`
- `metrics/`

Why it matters:

- Modern, readable LSM with strong separation among VFS, record/WAL, manifest, table, compaction, range-key/range-delete, and cache layers.
- `objstorage/` is highly relevant to object-backed filesystems: remote objects, shared cache, remote object catalog, readahead, and virtualized backing objects.

Exclude:

- `cmd/`, `bench/`, `metamorphic/`, `cockroachkvs/`, `internal/mkbench/`, `replay/`, tests and testdata.

Risk:

- Metamorphic tests are excluded from the source mirror, but they are valuable if the project later wants a compact correctness corpus.

### `engines/btree/wiredtiger`

Upstream: `https://github.com/wiredtiger/wiredtiger.git`

Verified branch/commit: `develop` at `8b8983d`

Include:

- `src/block/`
- `src/block_cache/`
- `src/block_disagg/`
- `src/btree/`
- `src/cache/`
- `src/checkpoint/`
- `src/checksum/`
- `src/conn/`
- `src/evict/`
- `src/history/`
- `src/include/`
- `src/live_restore/`
- `src/log/`
- `src/meta/`
- `src/os_common/`
- `src/os_darwin/`
- `src/os_linux/`
- `src/os_posix/`
- `src/os_win/`
- `src/reconcile/`
- `src/rollback_to_stable/`
- `src/schema/`
- `src/session/`
- `src/support/`
- `src/tiered/`
- `src/txn/`
- `src/utilities/`
- `ext/page_log/palite/`
- `ext/storage_sources/dir_store/`

Why it matters:

- Production B-tree/page/block system with eviction, checkpoints, logging, reconciliation, history store, rollback-to-stable, and metadata management.
- Strong contrast to LSM systems: page-oriented writeback, eviction pressure, checkpoint consistency, and history/version management.
- Tiered storage and extension storage sources are useful for object-backed and disaggregated filesystem research.

Exclude:

- `bench/`, `test/`, `examples/`, `lang/`, `dist/`, `src/docs/`, `ext/test/`.

Risk:

- WiredTiger has a larger internal support surface than the path list suggests. If later code reading hits unresolved dependencies, add specific `src/conf`, `src/cursor`, or `src/packing` files rather than broadening to full repository.

### `engines/page/sqlite`

Upstream: `https://github.com/sqlite/sqlite.git`

Verified branch/commit: `master` at `a5e5116`

Include:

- `src/btree.c`, `src/btree.h`, `src/btreeInt.h`
- `src/pager.c`, `src/pager.h`
- `src/pcache.c`, `src/pcache.h`, `src/pcache1.c`
- `src/wal.c`, `src/wal.h`
- `src/os.c`, `src/os.h`, `src/os_unix.c`, `src/os_win.c`, `src/os_kv.c`, `src/os_common.h`
- `src/memjournal.c`
- `src/malloc.c`
- `src/mutex.c`, `src/mutex.h`
- `src/fault.c`
- `src/backup.c`
- `ext/misc/appendvfs.c`
- `ext/misc/cksumvfs.c`
- `ext/misc/fileio.c`
- `ext/misc/pcachetrace.c`
- `ext/misc/tmstmpvfs.c`
- `ext/misc/vfslog.c`
- `ext/misc/vfsstat.c`
- `ext/misc/vfstrace.c`
- `ext/misc/zipfile.c`

Why it matters:

- The pager, WAL, rollback journal, page cache, and VFS are a compact source-level model of crash consistency.
- VFS examples expose the filesystem boundary: locking, checksums, timestamping, tracing, custom file implementations, and ZIP-like storage.

Exclude:

- SQL planner/executor, FTS/JSON extensions, `test/`, `mptest/`, `autoconf/`, `contrib/`, `ext/wasm/`.

Risk:

- SQLite's generated amalgamation is not needed. Use canonical source files so file-level boundaries remain visible.

### `engines/distributed/foundationdb`

Upstream: `https://github.com/apple/foundationdb.git`

Verified branch/commit: `main` at `aa6b602`

Include:

- `fdbserver/kvstore/`
- `fdbserver/logsystem/`
- `fdbserver/tlog/`
- `fdbserver/storageserver/`
- `fdbserver/datadistributor/`
- `fdbserver/core/`
- `fdbserver/commitproxy/`
- `fdbserver/resolver/`
- Selected blob, backup, range map, mutation log, checkpoint, storage interface, and version-vector files under `fdbclient/` and `fdbclient/include/fdbclient/`.

Key files to preserve even if narrowing later:

- `fdbserver/kvstore/DiskQueue.cpp`
- `fdbserver/kvstore/IPager.cpp`
- `fdbserver/kvstore/VFSAsync.cpp`
- `fdbserver/kvstore/VersionedBTree.actor.cpp`
- `fdbserver/kvstore/KeyValueStoreRocksDB.actor.cpp`
- `fdbserver/kvstore/KeyValueStoreSQLite.cpp`
- `fdbserver/logsystem/LogSystem.cpp`
- `fdbserver/tlog/TLogServer.cpp`
- `fdbserver/storageserver/storageserver.actor.cpp`
- `fdbserver/datadistributor/DataDistribution.cpp`
- `fdbclient/MutationLogReader.cpp`
- `fdbclient/StorageCheckpoint.cpp`
- `fdbclient/AsyncFileBlobStore.cpp`
- `fdbclient/S3BlobStore.cpp`
- `fdbclient/GCSBlobStore.cpp`

Why it matters:

- Distributed filesystem design needs durable logs, shard maps, movement, recovery, backup, snapshots, and storage-server behavior. FoundationDB has all of these in production-quality code.
- `kvstore/` includes multiple local store backends and async VFS concepts; `logsystem/` and `tlog/` show replicated transaction log service structure.

Exclude:

- `bindings/`, `layers/`, `tests/`, `documentation/`, `packaging/`, workloads, most client API and CLI code.

Risk:

- FDB uses Flow actor code and generated actor transformations. The source is still useful, but readers must understand that `*.actor.cpp` has a build-time transformation model.

### `engines/distributed/tikv`

Upstream: `https://github.com/tikv/tikv.git`

Verified branch/commit: `master` at `d9bfe79`

Include:

- `components/raftstore/src/`
- `components/raftstore-v2/src/`
- `components/raft_log_engine/src/`
- `components/engine_traits/src/`
- `components/engine_rocks/src/`
- `components/file_system/src/`
- `components/sst_importer/src/`
- `components/snap_recovery/src/`
- `components/compact-log-backup/src/`
- `components/backup-stream/src/`
- `components/backup/src/`
- `components/external_storage/src/`
- `components/cloud/src/`
- `components/cloud/aws/src/`
- `components/cloud/gcp/src/`
- `components/cloud/gcp_v2/src/`
- `components/cloud/azure/src/`
- `src/storage/`
- `src/server/raftkv/`
- `src/server/raftkv2/`

Why it matters:

- Raftstore and raftstore-v2 cover region split/merge, snapshot generation/apply, raft log GC, async I/O, consistency checks, PD heartbeats, recovery, and replicated metadata ownership.
- Engine traits and RocksDB wrapper show how a distributed KV server abstracts storage engines, snapshots, import, compaction, and filesystem-facing I/O.
- SST importer, backup stream, external storage, and cloud modules map to distributed filesystem bulk ingest and object-store integration.

Exclude:

- `components/test_*`, component tests/benches/examples, root `tests/`, `fuzz/`, `cmd/`, and `src/storage/kv/test_engine_builder.rs`.

Risk:

- TiKV depends on other PingCAP crates and RocksDB bindings. For source reading, keep the listed modules; for compilation, a separate dependency policy would be needed.

### `engines/distributed/raft-engine`

Upstream: `https://github.com/tikv/raft-engine.git`

Verified branch/commit: `master` at `29a4e7c`

Include:

- `src/`

Why it matters:

- Focused file-pipe raft log engine: log file format, readers, writers, file recycling, in-memory indexing, environment abstraction, and recovery.
- This should be read beside TiKV raftstore because it isolates durable raft log persistence from the wider KV server.

Exclude:

- `tests/`, `stress/`, `ctl/`, `examples/`.

Risk:

- Some design intent lives in tests and benchmarks. Keep them out of the primary source mirror, but add specific tests later if investigating log recycling or corruption recovery.

## Cross-Cutting Study Map

Read order for a filesystem researcher:

1. LevelDB: minimal LSM, WAL, SST, Env.
2. SQLite pager/VFS: crash consistency and filesystem boundary.
3. Pebble: modern LSM separation and object-storage abstraction.
4. RocksDB: production LSM complexity, blob files, persistent cache, backup/checkpoint.
5. Badger: value-log separation and log cleaning.
6. WiredTiger: page/B-tree/checkpoint/eviction alternative to LSM.
7. Raft Engine: standalone durable replicated log.
8. TiKV: replicated region storage, snapshots, raft log GC, SST ingest.
9. FoundationDB: distributed log system, storage servers, shard movement, checkpoints, backup, and recovery.

Mechanism-to-source index:

| Mechanism | Primary sources |
| --- | --- |
| WAL and record format | LevelDB `db/log_*`, RocksDB `db/log_*`, Pebble `record/` and `wal/`, SQLite `src/wal.c`, Raft Engine `src/file_pipe_log/` |
| SST/table format | LevelDB `table/`, RocksDB `table/`, Pebble `sstable/`, Badger `table/`, TiKV `components/sst_importer/src/` |
| LSM compaction | RocksDB `db/compaction/`, Pebble `internal/compact/` and top-level compaction files, Badger `compaction.go`, TiKV `engine_rocks` and raftstore compact workers |
| Page cache and pager | SQLite `src/pager.c`, `src/pcache*.c`; WiredTiger `src/cache/`, `src/evict/`, `src/btree/` |
| B-tree and block/page layout | SQLite `src/btree.c`; WiredTiger `src/btree/`, `src/block/`, `src/reconcile/` |
| VFS/file abstraction | SQLite `src/os*.c`, `ext/misc/*vfs*.c`; RocksDB `env/`, `file/`; Pebble `vfs/`; FDB `VFSAsync`; TiKV `components/file_system/src/` |
| Snapshots/checkpoints | RocksDB `utilities/checkpoint/`; Pebble checkpoint files; WiredTiger `src/checkpoint/`; FDB `StorageCheckpoint`; TiKV raft snapshots |
| Object/tiered storage | Pebble `objstorage/`; WiredTiger `src/tiered/`; FDB blob stores; TiKV external/cloud storage |
| Replicated log | Raft Engine `src/`; TiKV `components/raftstore*/`; FDB `logsystem/` and `tlog/` |
| Shard/region movement | FoundationDB `datadistributor/`, `storageserver/`; TiKV raftstore split/merge and PD workers |

## Omission Risks

- **Kernel/filesystem code is intentionally absent.** This candidate only covers storage engines; the full `learn_fs` target needs Linux/BSD FS code, FUSE examples, object stores, distributed filesystems, and userspace FS frameworks from other candidates.
- **Ceph/MinIO/SeaweedFS/juicefs-style object stores are absent.** They belong in an object/distributed filesystem candidate, not this storage-engine subset.
- **RocksDB dependencies and bindings are excluded.** Good for source reading; insufficient for standalone build.
- **SQLite SQL layers are excluded.** This keeps focus on pager/VFS. Add query layers only if studying how logical workloads stress pager behavior.
- **Tests are mostly excluded.** Crash-consistency tests are valuable but large. A second pass should selectively add tests such as SQLite WAL/pager tests, Pebble metamorphic tests, RocksDB db_stress seeds, and Raft Engine corruption tests.
- **Generated code is mostly excluded.** If a generated format struct is required to understand on-disk format, add only that file and document why.
- **FoundationDB actor build model adds cognitive overhead.** Keep `*.actor.cpp` sources because they are the authored logic, but do not treat this subset as directly buildable.
- **Default branches can move.** The commits above were verified on 2026-06-15; the final mirror should pin commit SHAs or vendor snapshots.

## Verification

Verification performed locally on 2026-06-15 using shallow, blobless official GitHub clones in `/tmp/learnfs-agent05-repos`.

Verified upstreams and heads:

| Repo | Branch | Commit | Candidate source files after coarse exclusions |
| --- | --- | --- | ---: |
| `facebook/rocksdb` | `main` | `c9252b9` | 827 |
| `google/leveldb` | `main` | `7ee830d` | 96 |
| `dgraph-io/badger` | `main` | `284cea0` | 50 |
| `cockroachdb/pebble` | `master` | `b658835` | 300 |
| `wiredtiger/wiredtiger` | `develop` | `8b8983d` | 364 |
| `sqlite/sqlite` | `master` | `a5e5116` | 32 |
| `apple/foundationdb` | `main` | `aa6b602` | 192 |
| `tikv/tikv` | `master` | `d9bfe79` | 406 |
| `tikv/raft-engine` | `master` | `29a4e7c` | 29 |

Total coarse candidate source files: 2296.

The file count is not a precise LOC measure. It was computed from Git trees by matching source extensions and excluding tests, docs, benchmarks, examples, CI, and generated/binding-heavy paths. Exact LOC was not computed because the verification clones used `--filter=blob:none`; reading every blob would trigger large on-demand downloads. For final import, run `cloc` or `tokei` after sparse checkout if exact line accounting is required.

Suggested final import command pattern:

```bash
git clone --filter=blob:none --sparse <upstream> <target>
git -C <target> sparse-checkout set <include paths from YAML>
git -C <target> checkout <verified_commit>
```

Then remove excluded files with a script driven by `agent05-storage-engines.yaml`, or use sparse patterns that only include exact file paths for narrow cases such as SQLite.
