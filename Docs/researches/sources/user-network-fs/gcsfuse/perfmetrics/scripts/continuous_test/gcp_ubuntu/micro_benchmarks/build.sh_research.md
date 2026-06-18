## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh

Purpose: Remotely runs micro-benchmark tests on a persistent GCE VM named `periodic-micro-benchmark-tests`.

APIs and control flow: Defines `log()` and `run_script_on_vm()`. The main path calls `sudo gcloud compute ssh` with `--internal-ip`, updates apt, installs git, unmounts an existing gcsfuse mount if present, deletes `~/github`, clones `GoogleCloudPlatform/gcsfuse`, checks out yesterday's last commit, and runs `perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh`.

State and persistence: Mutates the remote VM heavily: package cache, repository checkout, mount state, and benchmark outputs. Local script state is limited to stdout logs.

Dependencies and risks: Requires gcloud auth, SSH permission, VM availability, sudo, network access, and correct hard-coded zone/path values. It deletes `~/github` on the VM, so the VM must be dedicated.

Test signals: Exit status from remote command controls the build. Timestamped logs show progress.
