## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/zonal_distributed.cfg

Purpose: Kokoro config for zonal distributed benchmark on Ubuntu.

APIs and integration: Invokes `continuous_test/gcp_ubuntu/build.sh` with `BENCHMARK_TYPE=distributed_benchmark_zonal` and a 300-minute timeout.

Control flow and state: The file only configures job dispatch.

Dependencies and risks: It depends on the shared build script mapping the benchmark type to the correct zonal workload. Output capture is not declared locally.

Test signals: Successful Kokoro job execution is the primary validation.
