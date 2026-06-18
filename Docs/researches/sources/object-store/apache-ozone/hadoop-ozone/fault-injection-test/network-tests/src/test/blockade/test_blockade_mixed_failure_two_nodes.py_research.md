## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_two_nodes.py

Purpose: pytest scenarios where two datanodes have SCM communication failures, either in the same partition or different partitions.

Important APIs/types/functions: `test_two_dns_isolate_scm_same_partition` and `test_two_dns_isolate_scm_different_partition`.

Control flow: after Freon seeding, tests construct two or three blockade partitions, run Freon during failure, select containers from the datanode expected to have authoritative state, wait until a replica is quasi-closed or not open, assert accepted state combinations, restore network, wait for all closed, and verify Freon success.

State and persistence behavior: external network partitions and datanode on-disk container files. No durable test-local state.

Dependencies and integration points: uses `OzoneCluster` and its `Container` wrappers.

Risks: expected alternatives in the different-partition case show nondeterministic outcomes; direct string state comparisons can hide future state additions; no explicit cleanup if mid-test assertion fails beyond teardown.

Test signals: verifies same-partition SCM failures produce one quasi-closed and two open replicas; different partitions allow either all closed for connected replicas or open/quasi-closed combination before final closure.
