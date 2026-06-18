# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EnvOptions.java

Purpose: native file IO option wrapper used while opening files. It can be default-constructed or constructed from `DBOptions`.

APIs configure mmap reads/writes, direct reads/writes, fallocate, fd close-on-exec, bytes-per-sync, keep-size fallocate, compaction readahead, writable-file max buffer size, and a write `RateLimiter`. Control flow loads the RocksDB library for default allocation and forwards all fields to native methods. `setRateLimiter` stores a Java reference and passes its native handle, so state includes native options plus a retained limiter reference.

Persistence is indirect: options affect file-opening and IO behavior, not Java storage. Dependencies include `RocksObject`, `DBOptions`, and `RateLimiter`.

Risks: comments include platform-specific semantics; Java does no validation of direct/mmap compatibility; constructing from `DBOptions` depends on source options lifetime during the call; rate limiter lifetime is retained only after setter use. Tests should round-trip every option, construct from DBOptions, exercise direct IO/mmap combinations where supported, and validate limiter retention/disposal.
