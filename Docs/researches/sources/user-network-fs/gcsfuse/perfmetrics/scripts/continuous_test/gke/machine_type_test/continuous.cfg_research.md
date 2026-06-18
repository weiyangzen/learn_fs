## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/continuous.cfg

Purpose: Kokoro config for the GKE machine-type optimization test.

APIs and integration: Sets `BUCKET_NAME=gcsfuse_gke_machine_type_test_flat_euw4` and runs `gke/machine_type_test/run.py` as the build file.

Control flow and state: The Python script creates cloud resources, deploys a pod, and runs integration tests. This config only supplies the bucket default.

Dependencies and risks: Bucket IAM and Workload Identity setup must match the runner. No timeout or artifacts are declared locally.

Test signals: The runner's exit code and pod logs are the main validation.
