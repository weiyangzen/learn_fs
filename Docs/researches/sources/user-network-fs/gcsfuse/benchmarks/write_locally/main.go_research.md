## sources/user-network-fs/gcsfuse/benchmarks/write_locally/main.go

Purpose: Benchmark local repeated overwrites of a pre-sized file without closing between iterations, focusing on CPU/filesystem write path rather than remote flush throughput.

Important APIs/types/functions: flags `--dir`, `--duration`, `--file_size`, `--write_size`; `run()` creates temp file, truncates to file size, repeatedly seeks to start and writes zero buffers until duration, then reports write calls and throughput.

Control flow: require `--dir`; create temp file; defer truncate/close/remove; truncate to configured size; allocate zero buffer; timed loop seeks to start then writes until full file or duration; compute Hz and bytes/sec.

State and persistence: creates a temp file, overwrites it, truncates and removes it on normal exit.

Dependencies and integration points: exercises write path of the filesystem mounted at `--dir`; uses internal `format`.

Risks: `write_size <= 0` is not validated and can cause ineffective writes or panics. It does not call fsync or close during measured loop, so remote durability/flush costs are excluded by design. Last partial file pass is included in throughput.

Test signals: benchmark output; no unit tests.
