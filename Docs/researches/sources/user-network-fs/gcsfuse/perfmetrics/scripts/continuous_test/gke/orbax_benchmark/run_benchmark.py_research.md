## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/run_benchmark.py

Purpose: Runs the Orbax checkpoint load benchmark in a GKE pod and gates success on throughput.

APIs and control flow: `parse_all_gbytes_per_sec` extracts floats from log lines matching `gbytes_per_sec: <num> Bytes/s`. `execute_workload_and_gather_results` creates a ConfigMap from `test_load.py`, renders `pod.yaml.template`, applies it, polls pod phase until completion or timeout, reads logs, parses throughput, then deletes configmap/manifest. `main` parses env/CLI, sets up GKE and optionally builds CSI in parallel, executes the workload, and requires at least 5/8 of parsed iterations to meet `performance_threshold_gbps`.

State and persistence: Creates cluster resources via `common.utils`, Kubernetes ConfigMap/pod/manifest files, and optionally a CSI image. Cleanup may run both in error branches and `finally`.

Dependencies and risks: Regex unit label says `Bytes/s` while variables say GB/s. The fixed pod name `gcsfuse-test` can collide if parallel runs share a namespace. Cleanup deletes configmap without `check=False`, so missing configmap can mask earlier errors.

Test signals: Throughput count, threshold pass/fail message, and process exit status.
