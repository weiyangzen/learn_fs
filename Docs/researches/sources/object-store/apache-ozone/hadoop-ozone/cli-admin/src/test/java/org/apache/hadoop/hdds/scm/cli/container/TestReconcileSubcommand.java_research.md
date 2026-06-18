<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java

Purpose: Tests the container reconcile CLI for status and trigger modes across valid containers, mismatched replicas, stdin input, invalid IDs, EC/open container rejection, server-side failures, and authentication stop behavior.

Important APIs and types: `ReconcileSubcommand`, mocked `ScmClient`, `ContainerInfo`, `ContainerReplicaInfo`, `RatisReplicationConfig`, `ECReplicationConfig`, `LifeCycleState`, `AccessControlException`, Picocli `CommandLine`, Jackson JSON parsing, Mockito verification, and captured stdout/stderr.

Control flow: Setup mocks reconciliation RPCs and stream capture. Helpers parse args with `container reconcile`, execute status or trigger modes from args or stdin, create containers and replica sets, and validate JSON status output. Tests cover matching and mismatching data checksums, no input, mixing stdin and args, unsupported EC/open status, invalid reconcile RPCs, mixed valid/invalid batches, auth failure short-circuiting, invalid numeric IDs, and unreachable containers.

State and persistence behavior: No real SCM state. Mocked containers and replicas model SCM metadata; `reconcileContainer` side effects are verified by Mockito. JSON output is transient captured text.

Dependencies and integration points: Exercises command integration with SCM container metadata, replica checksum comparison, stdin convention, root CLI exit handling for auth failures, and error aggregation.

Risks: The command deliberately continues past some per-container failures but stops on authentication failure; tests guard that distinction. JSON validation uses parsed maps with integer casts, so schema changes can break tests. Server-side restrictions are partly mocked because actual validation lives in SCM.

Test signals: JSON arrays with `replicasMatch`, container state/replication fields, replica datanode maps and checksum hex strings, success trigger messages, aggregated failure counts, stderr not mentioning valid containers, auth failure verifies only first RPC, and invalid IDs produce no output for valid-looking IDs in the same batch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java -->
