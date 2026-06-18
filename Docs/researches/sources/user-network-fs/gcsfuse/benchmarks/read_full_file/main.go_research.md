## sources/user-network-fs/gcsfuse/benchmarks/read_full_file/main.go

Purpose: Benchmark full sequential file reads through a filesystem, including per-read latency and full-file throughput.

Important APIs/types/functions: flags `--dir`, `--duration`, `--file_size`, `--read_size`; `run()` creates random temp file content, repeatedly opens and reads it to EOF, records full-file and single-read durations, sorts observations, and reports p50/p90/p98 throughput via `format.Bytes` and `percentile.Duration`; `main()` parses flags and handles errors.

Control flow: require `--dir`; create temp file; write `file_size` bytes from `crypto/rand`; close; loop until duration elapsed with at least one full read; on each iteration open, read until EOF, measure per call and full file, close; sort; print reports; defer delete.

State and persistence: creates and deletes a temporary file under the target dir. The temp file may persist if process is killed before defer.

Dependencies and integration points: exercises the mounted filesystem under `--dir`; uses OS file APIs, crypto random source, internal format and percentile packages.

Risks: cryptographic random generation can dominate setup for large files. `read_size` is not validated for positive values. Read calls append a latency measurement for the EOF read too, which may skew per-call latency.

Test signals: benchmark output itself is the signal; no unit tests.
