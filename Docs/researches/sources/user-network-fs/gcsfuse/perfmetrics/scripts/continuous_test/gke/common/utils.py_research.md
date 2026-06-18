## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/utils.py

Purpose: Shared async command, prerequisite, GKE cluster, node-pool, network, cleanup, and gcsfuse CSI image build utilities for GKE benchmark scripts.

APIs and control flow: Key APIs are `run_command_async`, `check_prerequisites`, `setup_gke_cluster`, existence/health helpers for clusters and node pools, `create_node_pool_async`, `delete_node_pool_async`, `create_network`, `cleanup`, and `build_gcsfuse_image`. Commands are passed as argument lists to avoid shell injection in most helpers. `setup_gke_cluster` creates missing network/subnet/cluster/node pool, recreates unhealthy node pools, then fetches credentials.

State and persistence: Mutates the host by installing apt packages, adding Google Cloud apt sources, installing gcloud/kubectl/auth plugin/make, and mutates Google Cloud by creating/deleting clusters, node pools, VPCs, subnets, firewall rules, and container images.

Dependencies and risks: Requires sudo, apt, curl, gpg, gcloud, kubectl, make, git, Google Cloud auth, and quota/reservations. Cleanup deletes firewall rules by network filter and deletes the network/subnet, so name isolation is critical.

Test signals: No local unit tests in this subset. Consumers rely on command return codes and printed stdout/stderr.
