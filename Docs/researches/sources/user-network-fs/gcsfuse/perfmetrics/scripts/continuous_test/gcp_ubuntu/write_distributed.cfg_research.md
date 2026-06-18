## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/write_distributed.cfg

Purpose: Kokoro config for distributed write benchmark on Ubuntu.

APIs and integration: Delegates to the shared Ubuntu build script with `BENCHMARK_TYPE=distributed_benchmark_write` and a 300-minute timeout.

Control flow and state: No local logic; state and artifacts are controlled by the build script.

Dependencies and risks: Exact env var value is the integration contract. Missing artifact definitions can make performance-debug evidence unavailable unless inherited elsewhere.

Test signals: Expected signal is successful execution of the write benchmark branch.
