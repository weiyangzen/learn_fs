## sources/user-network-fs/gcsfuse/benchmarks/write_to_gcs/main.go

Purpose: Benchmark writing a new file and closing it, separating write-call time from close/flush time to approximate CPU path and GCS upload finalization.

Important APIs/types/functions: flags `--dir`, `--file_size`, `--write_size`; `run()` creates temp file, writes zero buffers until target size, measures write duration, closes and measures close duration, prints throughput for both phases.

Control flow: require `--dir`; create temp file; defer delete; allocate zero buffer; loop until `bytesWritten >= file_size`, using `min` to compute intended write size but writing the full buffer; measure close; print reports.

State and persistence: creates a temp file under the mounted directory, closes it, then removes it on normal exit.

Dependencies and integration points: exercises mounted gcsfuse write and close paths; uses Go 1.21+ predeclared `min` and internal `format`.

Risks: computed `toWrite` is not used to slice the buffer, so if `file_size` is not a multiple of `write_size`, the program writes more bytes than requested while incrementing by the smaller remainder. `write_size <= 0` is not validated. Delete after close may itself trigger remote work outside reported timing.

Test signals: benchmark output; no unit tests. A targeted test should catch the final partial-write accounting issue.
