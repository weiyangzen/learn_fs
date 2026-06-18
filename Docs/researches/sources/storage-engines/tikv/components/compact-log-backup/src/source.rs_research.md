# sources/storage-engines/tikv/components/compact-log-backup/src/source.rs

Purpose: loads compact-log-backup input log segments from external storage, optionally through the physical-file cache, decompresses them, and iterates encoded key/value events for compaction.

Important APIs and types: `Source`, `Record`, `Source::new`, `cache_input_refs`, `load_remote`, `load`, `Record::cmp_key`, and `Record::ts`. Internal helpers `load_compressed` and `decompress` support Zstd-compressed BR log backup data.

Control flow: `load_remote` retries reads, first attempting `PhysicalFileCache::load_part` when configured, then falling back to `read_part` on external storage. It decompresses into memory and updates physical-byte/error stats. `load` parses the decompressed event stream with `EventIterator`, periodically yields via `Cooperate`, invokes a caller callback for each key/value pair, and updates logical input stats.

State and persistence: reads remote objects only. Optional cache references are RAII guards that reserve physical files while subcompactions need their segments.

Dependencies and integration: used by `SubcompactionExec` through `compaction::Input`. Depends on `ExternalStorage`, `PhysicalFileCache`, BR compression proto, TiKV stream-event codec, transaction timestamp decoding, and `LoadStatistic`.

Risks: only Zstd compression is supported here; other compression enum values return `Unsupported`. Entire segment contents are decompressed into memory, so subcompaction sizing and cache capacity matter. Callback execution happens inline and can affect cooperative scheduling.

Test signals: tests build synthetic Zstd log files, load each segment, verify keys/values and statistics, and validate cache reference release behavior.
