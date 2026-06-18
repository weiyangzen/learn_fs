## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh

Purpose: Runs installed-package gcsfuse integration tests against the TPC endpoint. It builds gcsfuse at a selected commit, configures a TPC gcloud universe, authenticates with a service account key copied from GCS, and runs `improved_run_e2e_tests.sh`.

APIs and control flow: The script takes no arguments and enforces `set -euo pipefail`. It installs latest gcloud, determines branch and commit, builds via `build_and_install_gcsfuse.sh`, checks out the tested commit, creates and activates a `prptst` gcloud configuration, sets TPC API endpoint overrides, runs tests with `--test-on-tpc-endpoint`, then restores default gcloud config and exits with the captured test status.

State and persistence: It mutates the local git checkout, gcloud configurations, `/tmp/sa.key.json`, and installed gcsfuse package. Daily Kokoro scheduler runs use yesterday's final master commit; manual runs use HEAD.

Dependencies and risks: Depends on Kokoro env vars, GCS credential bucket access, gcloud storage, Git, and TPC endpoint availability. Cleanup is best-effort after tests; failures before the final restore can leave gcloud config altered.

Test signals: Exit code reflects integration-test result. Logs from build failure are printed from a temp file.
