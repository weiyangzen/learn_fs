# Research: sources/storage-engines/rocksdb/include/rocksdb/universal_compaction.h

- **Purpose:** Defines public configuration for universal compaction picking and limits.
- **Important APIs/types/functions:** `CompactionStopStyle` selects similar-size or total-size file picking. `CompactionOptionsUniversal` fields include `size_ratio`, `min_merge_width`, `max_merge_width`, `max_size_amplification_percent`, `compression_size_percent`, `max_read_amp`, `stop_style`, `allow_trivial_move`, `incremental`, and `reduce_file_locking`, with a default constructor and defaulted equality operator.
- **Control flow:** Universal compaction logic reads these options to decide when files are compacted, how many sorted runs to tolerate, whether output should be compressed, whether trivial moves are allowed, and whether to adjust file picking when bottom-priority compactions wait.
- **State and persistence:** Options are runtime configuration and can affect future compaction outputs; they are not direct persisted metadata. Some choices influence file layout and compression of new SSTs.
- **Dependencies:** Uses basic integer/vector headers and the RocksDB namespace.
- **Integration points:** Consumed by column-family compaction options and dynamic `SetOptions()` for `reduce_file_locking`.
- **Risks:** Invalid `max_read_amp` values can cause `Status::NotSupported()` at DB open. Aggressive `max_size_amplification_percent`, `incremental`, or file-locking reduction can trade read amplification, write amplification, and compaction load. Some automatic behavior only applies with total-size stop style.
- **Test signals:** Tests should cover default values, option equality, DB-open validation, compaction-picking boundaries, compression-size thresholds, trivial-move behavior, and dynamic `reduce_file_locking` updates.
