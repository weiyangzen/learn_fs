<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py

## Purpose

`block_cache_pysim.py` is a standalone Python simulator for RocksDB block-cache trace CSVs. It evaluates replacement and admission behavior across trace-observed hits, LRU-style policies, Belady MIN, ARC, GreedyDualSize, and reinforcement-learning policy selectors. It also emits CSV fragments for miss-ratio curves, miss and miss-ratio timelines, byte-miss summaries, and policy-selection timelines consumed by the shell combiner and plotting script in this same directory.

## Important APIs, Types, And Functions

`TraceRecord` mirrors the fields of RocksDB `BlockCacheTraceRecord` as a CSV-friendly Python object. It normalizes boolean integer fields and computes the effective cached block size as `block_size + block_key_size`.

`CacheEntry`, `HashEntry`, and `HashTable` provide the storage primitives used by sampled policies. `HashTable` is a custom chained hash table with resize-on-growth/shrink and `random_sample()` for sampled eviction. This supports ML policy evaluation without materializing or sorting the whole cache on each eviction.

`MissRatioStats` and `PolicyStats` accumulate global and time-bucketed counters. `MissRatioStats` tracks accesses, misses, miss bytes, and per-time-unit maps; `PolicyStats` records the policy chosen by an ML cache per time bucket.

`Policy` and its implementations (`LRUPolicy`, `MRUPolicy`, `LFUPolicy`, `HyperbolicPolicy`, `CostClassPolicy`) rank sampled entries for eviction. `ThompsonSamplingCache` and `LinUCBCache` choose among these policies using bandit-style reward from whether a selected policy had evicted the missed key.

`Cache` is the abstract simulator base. `access()` handles block-vs-row-key behavior, calls `_lookup()`, `_evict()`, `_insert()`, and `_should_admit()`, and updates the common miss statistics. `MLCache`, `OPTCache`, `GDSizeCache`, `ARCCache`, `LRUCache`, and `TraceCache` implement the policy-specific mechanics.

`create_cache()` is the main factory. It parses `hybrid` and `hybridn` suffixes, scales capacity by downsample ratio, and maps strings such as `ts`, `linucb`, `pylru`, `pycctbbt`, `opt`, `trace`, `lru`, `arc`, and `gdsize` to concrete cache instances.

`run()` is the trace driver. It optionally pre-scans the whole trace for OPT next-access sequence numbers, streams each CSV line into a `TraceRecord`, filters by column family, handles warmup counter reset, updates trace-observed stats, and feeds the selected simulator. `report_stats()` writes the generated `data-ml-*` files. The `__main__` block parses eight CLI arguments and wires the factory, runner, and reporter together.

## Control Flow

The CLI expects cache type, cache size, downsample size, warmup seconds, trace path, result directory, max accesses, and target column family. It parses capacity suffixes with `parse_cache_size()`, creates a cache, streams the trace through `run()`, then writes summaries with `report_stats()`.

For normal policies, `run()` is single pass: split each comma-delimited line, skip non-target column families, create a `TraceRecord`, update observed trace stats, and call `cache.access()`. For `OPTCache`, `run()` first scans all target records into per-block `BlockAccessTimeline` instances so every later access can carry `next_access_seq_no` for Belady-style eviction.

`Cache.access()` either routes Get-like records through row-key hybrid handling or directly accesses the block key. `_access_kv()` performs the generic lookup/miss/admission sequence. Policy implementations only supply lookup/eviction/insertion details, keeping metric update centralized.

Hybrid row-key mode treats `caller == 1` records with nonzero `get_id` and `key_id` as Gets. It first attempts the row key, may short-circuit future block accesses for the same Get when a row hit completes the request, and can run in mode `2` where data blocks are not inserted on row misses.

## State And Persistence Behavior

Runtime state is in-memory and proportional to cache contents plus trace metadata. `HashTable` keeps cache entries for sampled policies; `PQTable` backs OPT and GreedyDualSize; ARC keeps T1/T2/B1/B2 deques and a value table; hybrid mode keeps a bounded `get_id_row_key_map` with `retain_get_id_range = 100000`.

OPT can be memory-heavy because it keeps an access timeline for every block before replay. The code periodically calls `gc.collect()` during large runs and after hash-table resize to reduce Python heap pressure.

Persistent output is a family of CSV fragment files under `result_dir`, mostly prefixed `data-ml-...` and `header-ml-...`. `report_stats()` writes miss-ratio curves, per-second/minute/hour byte-miss summaries, miss timelines, miss-ratio timelines, and policy timelines for ML caches. It overwrites existing fragment files with `w+`.

## Dependencies And Integration Points

The script depends on Python standard modules plus `numpy`. It integrates with `block_cache_pysim.sh`, which launches many instances and concatenates the generated `header-` and `data-` files into aggregate `ml_*` files. Its output naming is also consumed by `block_cache_trace_analyzer_plot.py`.

The trace input format is assumed to be the comma-separated, human-readable ordering of RocksDB block-cache trace fields: timestamp, block id, block type, block size, column family metadata, caller, no-insert, Get/key metadata, hit flags, table/sequence/key-size metadata, and block offset.

## Risks And Edge Cases

Several policy paths are not Python 3 compatible as written. The file has a Python 3 shebang but uses `sorted(..., cmp=...)`, and `heapq` entries only define `__cmp__`, not `__lt__`; these paths fail under modern Python 3 when exercised. This affects sampled policy ranking and OPT/GDSize priority queues.

Some capacity arithmetic uses `/`, producing floats in Python 3 (`cache_size / downsample_size`, ARC `self.c`), while several cache algorithms compare sizes and lengths as if integers. This can produce subtle boundary differences or type surprises.

`PolicyStats.write_policy_ratio_timeline()` takes a `file_path` parameter but references `result_dir`, which is not local or global in that scope. `report_stats()` calls it, so ML cache reporting can raise `NameError`.

The CSV parser is positional and unescaped; a malformed line, missing field, or unexpected comma in a text field will fail or corrupt interpretation. `max_accesses_to_process` uses `access_seq_no > max`, so it processes one more record than a strict inclusive/exclusive caller might expect.

Cost-class accounting has suspicious calculations: `CostClassEntry.avg_size()` returns an average last-access time instead of size, and `remove()` subtracts hits, which can make cost-class hit totals negative depending on eviction sequence.

## Test Signals

`block_cache_pysim_test.py` directly imports and exercises the major cache classes, hash table behavior, row-key hybrid behavior, trace-observed stats, and an end-to-end synthetic trace. The tests are useful signals for intended semantics, especially expected evictions for LRU/LFU/MRU/OPT and cache-size accounting. However, because several Python 3-incompatible constructs are in active paths, the test module itself is also likely to expose runtime failures when run with the shebang's interpreter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py -->
