# sources/storage-engines/foundationdb/packaging/docker/run_ycsb_standalone.sh

Purpose: This script runs the same YCSB FoundationDB workload outside Kubernetes. It creates an FDB cluster file from environment variables, then launches YCSB.

Important functions: `create_cluster_file` mirrors the Docker server script: it writes `FDB_CLUSTER_FILE` from explicit contents, DNS-resolved coordinator and port, or exits with an error. The main path runs `./bin/ycsb.sh "$MODE" foundationdb -s -P workloads/$WORKLOAD $YCSB_ARGS`.

Control flow: Strict mode and an error trap print run metadata and environment. It logs workload start, creates the cluster file, runs YCSB, then logs completion.

State and persistence behavior: It writes a cluster file to the configured path and YCSB may write local benchmark artifacts. No S3 upload occurs in this standalone variant.

Dependencies and integration points: It depends on `dig`, YCSB, FoundationDB Java binding configuration, and environment variables for coordinator and workload selection.

Risks: Like the Kubernetes version, `YCSB_ARGS` quoting can collapse multiple arguments. DNS lookup failures abort the run. Tests should cover cluster-file-content override, coordinator path, missing coordinator failure, and a small workload smoke test.
