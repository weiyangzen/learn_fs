## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/read_distributed.cfg

Purpose: Kokoro config for distributed read benchmark on Ubuntu.

APIs and integration: Sets a 300-minute timeout, calls `continuous_test/gcp_ubuntu/build.sh`, and passes `BENCHMARK_TYPE=distributed_benchmark_read`.

Control flow and state: All benchmark behavior is delegated to the shared build script.

Dependencies and risks: Relies on the build script's dispatch table recognizing the exact benchmark type string. No artifacts are declared here, so output retention depends on shared or external Kokoro config.

Test signals: Successful run should complete within 300 minutes and execute the read workload path.
