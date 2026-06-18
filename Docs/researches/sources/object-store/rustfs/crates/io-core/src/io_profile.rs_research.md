# sources/object-store/rustfs/crates/io-core/src/io_profile.rs

Purpose: storage-media and access-pattern helpers for adaptive scheduling and buffer sizing.

Important APIs/types: `StorageMedia` parses/prints `Nvme`, `Ssd`, `Hdd`, `Unknown`. `AccessPattern` identifies sequential/random/mixed/unknown with helper predicates. `StorageProfile::for_media` maps media to buffer caps and multipliers. `IoPatternDetector` records `(offset, len)` history and classifies the current access pattern. `detect_storage_media` honors override strings and otherwise uses platform-specific detection.

Control flow: `IoPatternDetector::record` keeps a bounded history. `current_pattern` compares consecutive offsets against previous end plus tolerance and counts sequential versus random transitions. Linux detection checks `/sys/class/nvme` and a small fixed set of `/sys/block/*/queue/rotational` devices. macOS detection shells out to `diskutil info /`; other platforms return unknown.

State and persistence: detector state is in-memory `VecDeque` history. Storage detection reads OS files or command output but does not persist results.

Dependencies and integration: standard library only. The scheduler and example use these types to pick buffer sizes and behavior.

Risks: Linux detection samples only common device names and does not map a specific data path to its backing device, so container/multi-disk systems may be misclassified. macOS defaults to SSD for modern systems if no explicit signal appears. Pattern detection is local and sensitive to chosen history size/tolerance.

Test signals: tests cover override parsing, disabled detection, pattern classifications, helper predicates, storage profile values, and platform detection smoke tests.
