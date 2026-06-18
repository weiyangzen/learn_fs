## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_scm_isolation.py

Purpose: pytest coverage for datanodes that can communicate with peers but not SCM.

Important APIs/types/functions: `test_scm_isolation_one_node` and `test_scm_isolation_two_node`.

Control flow: tests seed data, partition a subset of datanodes away from SCM, run Freon during the partition, fetch containers from a SCM-connected datanode, wait for two closed replicas or a non-open state, assert the allowed states, restore network, wait for all closed, and run Freon again.

State and persistence behavior: uses blockade network partition state and reads Ozone container state from datanode disk metadata.

Dependencies and integration points: imports `OzoneCluster`; uses `OzoneClient.run_freon` and `Container` polling helpers.

Risks: the two-node expectation permits either quasi-closed/open or closed/closed outcomes, indicating timing or algorithm sensitivity; fixed polling windows may be insufficient under slow CI.

Test signals: confirms SCM isolation does not prevent the connected majority from closing replicas and that all replicas converge to closed after healing.
