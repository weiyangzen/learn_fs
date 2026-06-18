## sources/storage-engines/pebble/tool/db_analyze_metadata.go

Purpose: implements `db analyze-metadata`, a live SSTable metadata sampler that estimates per-level distributions for file size, blob-referenced size, KV counts, bytes per KV, key-prefix sharing, index/filter size, data blocks, two-level-index usage, and totals.

Important APIs/types/functions: `stat` combines `metricsutil.Welford` with a t-digest builder for mean/stddev and percentile estimates. `levelStats` groups per-level counters and `stat` values. `metadataStats` holds `manifest.NumLevels` entries. `runAnalyzeMetadata` replays the current version, builds level-separated physical SSTable lists, round-robin samples without replacement, and periodically prints. `processSSTableMetadata` opens each table through an object provider and records metadata. `printMetadataStats` renders an ASCII table with compact humanized values, standard-deviation percentages, p90/max lines, and per-level totals.

Control flow: the command uses `readCurrentVersion`, opens an object provider for the DB directory, skips virtual tables, and initializes total-file counts. The sampling loop checks timeout and sample-percent limits, reports every ten seconds or at stop, selects the next non-empty level round-robin, randomly removes one table from that level, processes it, and continues after per-file read errors.

State and persistence: no new files are written. All statistics are in-memory and progressively emitted to stdout. The DB is not opened as a `pebble.DB`; persistence is observed by manifest replay plus table object reads.

Dependencies and integration: integrates `db.go` manifest replay and options, `manifest.TableMetadata`, `objstorageprovider`, `sstable.Reader`, Cockroach `crbytes`/`crhumanize`, Pebble ASCII table rendering, t-digest, Welford statistics, and comparer split-prefix logic.

Risks: virtual tables are skipped, so virtualized workloads may be underrepresented. Per-file failures are logged but do not reduce `totalTables`, affecting sampled percentage. The loop reports only on timeout/sample/exhaustion or 10-second intervals, so very short non-TTY runs with no stopping condition rely on eventual exhaustion. Common-prefix calculation depends on the comparer split function.

Test signals: `db_analyze_metadata_test.go` constructs synthetic stats for empty, unsampled, small, large, zero-valued, and two-level-index cases and verifies formatted output through datadriven goldens.
