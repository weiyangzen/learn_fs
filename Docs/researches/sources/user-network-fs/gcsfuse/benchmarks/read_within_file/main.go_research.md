## sources/user-network-fs/gcsfuse/benchmarks/read_within_file/main.go

Purpose: Benchmark repeated random or sequential reads within an existing file.

Important APIs/types/functions: flags `--file`, `--random`, `--duration`, `--read_size`; `readRandom(io.ReaderAt, fileSize, readSize, duration)` performs random `ReadAt`; `readSequential(io.ReadSeeker, readSize, duration)` loops `Read` and seeks to start at EOF; `run()` opens the file, gets size, and dispatches by mode.

Control flow: require `--file`; open and seek to end for size; random mode validates file size and loops random offsets until duration; sequential mode reads until EOF then seeks to zero and continues; both print counts, bytes, duration, and rates.

State and persistence: read-only against the target file; advances file offset during sequential benchmark.

Dependencies and integration points: targets a mounted gcsfuse file or any filesystem file; uses internal `format`.

Risks: `math/rand` is not seeded, so random offset sequence is deterministic. `read_size <= 0` is not validated. Random offset uses `rand.Int63n(fileSize-readSize)`, excluding the final possible offset and panicking if equal sizes produce zero argument. Sequential loop increments read count even for EOF iterations.

Test signals: no unit tests; benchmark output validates operational behavior.
