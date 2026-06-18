## sources/test-tools/kdevops/workflows/minio/scripts/run_benchmark_suite.sh

Purpose: Runs a comprehensive MinIO Warp benchmark suite across mixed, get, put, delete, list, small-object, large-object, and high-concurrency workloads.

Important APIs/types/functions: Functions include `parse_duration_to_seconds` and `run_benchmark`. CLI positional inputs are host, access key, secret key, and total duration.

Control flow: Converts total duration to seconds, derives a per-test duration with a minimum of 30 seconds, creates `/tmp/warp-results`, then calls `warp` eight times with workload-specific concurrency/object size and JSON output redirected to timestamped files.

State and persistence: Writes result JSON/stdout files under `/tmp/warp-results`; leaves benchmark buckets because `--noclear` is used.

Dependencies and integration points: Requires the `warp` CLI, network access to MinIO, valid credentials, and MinIO bucket permissions. Intended to feed the MinIO report scripts.

Risks and test signals: Output filenames use only test type and one shared timestamp, so repeated `mixed` tests overwrite each other within a run. Test by running a short suite and counting result files; expected eight workloads may produce fewer files due to collisions.
