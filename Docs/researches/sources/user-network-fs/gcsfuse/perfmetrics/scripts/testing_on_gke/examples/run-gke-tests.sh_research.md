<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh

## Purpose
Standalone end-to-end GKE performance test harness for deploying fio/dlio workloads with the GCSFuse CSI driver, optionally building a custom CSI driver from local gcsfuse code.

## Important APIs, Types, And Functions
Large shell entry point controlled by environment variables. Key functions include `create_unique_experiment_id`, `verify_csi_driver_image`, `installDependencies`, `ensureGkeCluster`, `createCustomCsiDriverIfNeeded`, `deployAllFioHelmCharts`, `deployAllDlioHelmCharts`, `waitTillAllPodsComplete`, `fetchAndParseFioOutputs`, and `fetchAndParseDlioOutputs`.

## Control Flow
Validates env config, installs local tooling, authenticates gcloud, creates or updates GKE resources, prepares namespace/KSA, ensures source repos, optionally builds and publishes gcsfuse plus CSI image, deploys Helm charts, monitors pods until completion or timeout, cleans pods, and parses outputs to CSV/BigQuery. In `only_parse` mode it skips creation/deployment and only monitors/parses an existing experiment.

## State And Persistence Behavior
Creates clusters/node pools/namespaces/service accounts, builds images, writes binaries to GCS, clones repos, creates venv/tool installs, deploys/uninstalls Helm charts, mounts zonal buckets for output download, writes `fio/output.csv` and `dlio/output.csv`, and uploads parsed metrics.

## Dependencies
Requires gcloud, kubectl, helm, Docker, Go, jq, Python requirements, GKE APIs, GCS buckets, CSI driver repo, gcsfuse repo, and workload config JSON.

## Integration Points
Lives under `testing_on_gke/examples` and calls the fio/dlio chart generators and parsers in sibling directories. It is also referenced from presubmit paths for GKE benchmarks.

## Risks And Edge Cases
Mutates cloud resources, can run for a week by default, uses many unquoted shell expansions, and contains force-update code that may reset local repos when requested. Zonal output download relies on temporary gcsfuse mounts.

## Test Signals
No shell tests in this subset; runtime validation is via successful pod completion and parser output generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh -->
