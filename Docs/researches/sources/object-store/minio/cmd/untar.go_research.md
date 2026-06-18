# sources/object-store/minio/cmd/untar.go

Purpose: streams tar archives, optionally compressed with several formats, into object uploads through a caller-supplied `putObject` callback. It is used when MinIO needs to ingest archive contents as individual objects.

Important APIs and types: `detect` identifies compression by magic headers. `format` enumerates unknown, gzip, zstd, LZ4, S2, and BZ2. `untarOptions` controls directory handling, error tolerance, and prefixing. `disconnectReader` wraps an upstream reader so it can be closed to prevent further reads. `untar` is the main archive extraction function. `bz2Limiter` caps bzip2 concurrency at about half `GOMAXPROCS`.

Control flow: `untar` wraps the input in `bufio.Reader`, detects compression, installs the appropriate decompressor, then iterates `tar.Reader.Next`. It normalizes entry names, skips root entries and symlinks/unsupported types, optionally appends a directory slash, and applies `prefixAll`. Small files (`<= xioutil.MediumBlock`) are fully read into pooled memory and uploaded asynchronously with a 16-slot semaphore. Larger entries stream synchronously through `disconnectReader`. If `ignoreErrs` is false, the loop checks the first async error before continuing and returns sync errors immediately; otherwise errors are logged with `s3LogIf`.

State and persistence: the function does not persist directly; persistence is delegated to `putObject`. It uses pooled buffers for medium objects and goroutines for concurrent small uploads. Header modification time is normalized to `time.Now()` for non-positive large-file modtimes to avoid invalid resulting objects.

Dependencies and integration points: depends on archive/tar, gzip/zstd/lz4/s2/bzip2 libraries, MinIO `xioutil.ODirectPoolMedium`, path helpers (`pathJoin`, `trimLeadingSlash`, `slashSeparator`), and caller-provided object upload logic.

Risks: tar path handling must prevent unexpected absolute/root names; this code cleans and trims leading slashes but still trusts callback-level object semantics. Async small-file uploads require careful error propagation and buffer lifetime management. For small files with invalid modtime, no modtime normalization occurs before `header.FileInfo()` is passed, unlike the large-file path. Decompression limits are explicit for zstd window size and bzip2 concurrency, but archive bombs can still produce many entries.

Test signals: no local tests here. Valuable tests would cover all compression magic headers, symlink skipping, directory ignore/prefix behavior, async error propagation, context cancellation for bzip2, path normalization, and mixed small/large entries.
