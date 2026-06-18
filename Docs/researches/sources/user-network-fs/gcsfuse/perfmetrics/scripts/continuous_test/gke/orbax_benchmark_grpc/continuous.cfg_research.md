## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark_grpc/continuous.cfg

Purpose: Kokoro config for the gRPC variant of the GKE Orbax benchmark.

APIs and integration: Sets the same `BUCKET_NAME` as the default job, overrides `CLIENT_PROTOCOL=grpc`, and uses separate cluster/network/subnet names to isolate resources from the HTTP job. Runs `orbax_benchmark/run_benchmark.py`.

Control flow and state: The protocol value is passed into the pod template by the Python runner.

Dependencies and risks: Resource names must remain unique if jobs run concurrently. Benchmark comparison relies on all other defaults matching the HTTP config.

Test signals: Same as the Orbax runner, but with gRPC protocol in pod manifest.
