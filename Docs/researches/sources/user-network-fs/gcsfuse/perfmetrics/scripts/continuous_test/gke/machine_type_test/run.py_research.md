## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run.py

Purpose: Orchestrates a GKE TPU machine-type integration test verifying that CSI driver passes machine type to gcsfuse and gcsfuse enables expected optimization flags.

APIs and control flow: Functions include `set_up_bucket_permissions`, `is_tpu_machine_type`, `execute_test_workload`, and async `main`. `main` parses CLI/env defaults, appends zone to default network/subnet names, checks prerequisites, optionally builds the CSI image in parallel with cluster setup, grants bucket IAM to the default KSA principal, creates a timestamped pod manifest from `pod_tpu.yaml.template`, streams pod logs, checks final pod phase, cleans configmap/manifest/pod resources, and optionally deletes cloud infrastructure.

State and persistence: Creates GKE clusters, node pools, networks, IAM bucket bindings, Kubernetes configmaps/pods, temp manifests, and possibly a CSI image. `--no_cleanup` preserves cloud resources.

Dependencies and risks: Requires TPU-compatible machine types; non-TPU types raise `ValueError`. Pod status parsing strips quotes from kubectl JSONPath output. Cleanup references `manifest_filename` in `finally` after manifest creation; failures before assignment could be fragile.

Test signals: Success requires pod phase `Succeeded`; `run_test.sh` performs the in-pod Go integration tests.
