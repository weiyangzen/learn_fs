## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/continuous.cfg

Purpose: Kokoro config for the default HTTP GKE Orbax benchmark.

APIs and integration: Sets `BUCKET_NAME=llama_europe_west4` and dispatches to `gke/orbax_benchmark/run_benchmark.py`.

Control flow and state: The Python runner handles GKE setup, image build, pod execution, throughput parsing, and cleanup.

Dependencies and risks: Bucket must contain or expose the checkpoint path expected by the pod template/test script. No client protocol override means the runner default `http1` is used.

Test signals: Runner success depends on parsed throughput threshold.
