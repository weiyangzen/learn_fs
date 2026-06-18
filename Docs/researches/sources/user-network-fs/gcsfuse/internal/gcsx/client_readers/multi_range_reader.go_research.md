<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go

Purpose: adapter from `gcsx.GCSReaderRequest` to the shared `MultiRangeDownloaderWrapper` for random or rapid-bucket reads.

Important APIs/types/functions: type `MultiRangeReader`; constructor `NewMultiRangeReader`; methods `readFromMultiRangeReader`, `ReadAt`, and `destroy`.

Control flow: `ReadAt` returns `io.EOF` when offset is beyond object size unless skip-size checks are enabled, otherwise delegates to `readFromMultiRangeReader`. The delegate validates wrapper presence, increments wrapper ref count once using an atomic compare-and-swap, then calls wrapper `Read` with offset/end, metrics, tracing, and force-create flag. `destroy` decrements ref count if MRD was in use.

State and persistence behavior: no persistent state. In-memory state includes object metadata, MRD wrapper pointer, atomic `isMRDInUse`, metric handle, and trace handle. Reference count state lives in the shared wrapper.

Dependencies and integration points: used by `GCSReader` for random rapid-bucket reads and skip-size-check reads. Integrates `MultiRangeDownloaderWrapper`, metrics, tracing, logger, and GCS object metadata.

Risks: nil wrapper is an explicit error. Reference counting must be balanced on destroy; repeated reads share a single increment. Offset validation differs when `SkipSizeChecks` is true, which is needed for reads beyond cached object size.

Test signals: companion tests cover full and partial reads, nil wrapper error, zero-byte read, skip-size-check behavior, and invalid offset EOF.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go -->
