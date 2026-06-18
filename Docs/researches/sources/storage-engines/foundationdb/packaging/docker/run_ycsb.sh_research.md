# sources/storage-engines/foundationdb/packaging/docker/run_ycsb.sh

Purpose: This script is the Kubernetes-context entrypoint for the YCSB FoundationDB benchmark image. It waits for peer YCSB pods, runs the requested workload, and uploads histogram files to S3.

Important operations: It reads the current namespace from the service account, waits until pods with labels `name=ycsb,run=$RUN_ID` are running, runs `./bin/ycsb.sh "$MODE" foundationdb -s -P workloads/$WORKLOAD $YCSB_ARGS`, then syncs `/tmp/histogram.*` to `s3://$BUCKET/ycsb_histograms/$namespace/$POD_NAME` with KMS SSE.

Control flow: Strict mode and an error trap print run metadata and environment on failure. Logging uses UTC timestamps. The script blocks before running until the requested `NUM_PODS` are running.

State and persistence behavior: YCSB writes local temporary histograms, and the script persists them to S3. It does not create an FDB cluster file; the container environment is expected to supply dynamic client configuration.

Dependencies and integration points: It depends on Kubernetes service-account files, `kubectl`, AWS CLI, YCSB, and environment variables such as `RUN_ID`, `WORKLOAD`, `MODE`, `NUM_PODS`, `POD_NAME`, and `BUCKET`.

Risks: The pod readiness loop parses `kubectl` output with `grep -cv NAME`, which is fragile. Unquoted `$YCSB_ARGS` is passed as one shell word because it is inside quotes, limiting multi-arg behavior. Tests should run in a test namespace, verify wait logic, workload execution, failure trap output, and S3 upload path.
