## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_client_failure.py

Purpose: pytest scenarios for client-side write behavior when the client can reach only a subset of datanodes during container replication.

Important APIs/types/functions: module-level `setup_function` creates and starts `OzoneCluster`; `teardown_function` stops it. Tests are `test_client_failure_isolate_two_datanodes` and `test_client_failure_isolate_one_datanode`.

Control flow: each test seeds data with Freon, partitions OM/SCM/client with selected datanodes, writes a key from the client, inspects created containers and replica states, restores the network, waits for closure, and reruns Freon to prove the cluster still accepts workload. The one-datanode case also checks output text with regex and sleeps while the isolated datanode becomes stale.

State and persistence behavior: creates volumes/buckets/keys and container replicas in dockerized Ozone. Network state is mutated via blockade and restored during the test.

Dependencies and integration points: imports `OzoneCluster`, `ozone.util`, `re`, `time`, and logging. Uses `OzoneClient` APIs via `cluster.get_client()`.

Risks: fixed sleeps and output regexes can be brittle; the global `cluster` requires setup success; assertions assume a three datanode cluster and particular container state timing.

Test signals: asserts client-visible failure or success under partition, replica `OPEN/QUASI_CLOSED/CLOSED` states, and post-heal Freon success.
