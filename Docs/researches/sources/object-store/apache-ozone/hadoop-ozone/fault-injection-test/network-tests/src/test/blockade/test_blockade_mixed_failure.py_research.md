## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure.py

Purpose: pytest scenarios combining datanode peer isolation with SCM isolation for one datanode.

Important APIs/types/functions: `test_one_dn_isolate_scm_other_dn` and `test_one_dn_isolate_other_dn`, plus standard setup/teardown.

Control flow: both tests seed data with Freon, build multiple partition sets containing OM/SCM/client/datanodes in different combinations, run Freon during the partition, inspect containers from a selected datanode, wait for quasi-closed or closed states, assert allowed state combinations, restore network, wait for all replicas closed, and rerun Freon.

State and persistence behavior: mutates blockade partitions and Ozone container metadata. Test state is entirely in dockerized cluster runtime.

Dependencies and integration points: relies on `OzoneCluster`, `OzoneClient.run_freon`, and `Container` wait methods.

Risks: expected outcomes are tightly coupled to current Ozone close/quasi-close algorithms; multiple overlapping partition sets are hard to reason about; direct state reads can race with recovery.

Test signals: mixed failures should produce specific `QUASI_CLOSED`, `OPEN`, and `CLOSED` combinations during isolation, then all `CLOSED` after healing.
