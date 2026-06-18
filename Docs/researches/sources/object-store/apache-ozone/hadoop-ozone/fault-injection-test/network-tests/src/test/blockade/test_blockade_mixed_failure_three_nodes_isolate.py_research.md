## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_three_nodes_isolate.py

Purpose: pytest scenarios for all three datanodes isolated from each other, with zero, one, two, or three datanodes also unable to communicate with SCM.

Important APIs/types/functions: tests are `test_three_dns_isolate_one_scm_failure`, `test_three_dns_isolate_two_scm_failure`, and `test_three_dns_isolate_three_scm_failure`.

Control flow: each test starts from Freon-created data, partitions each datanode into its own group with OM/client and optional SCM reachability, waits on a representative container state, asserts per-datanode replica states, restores the network, waits for all replicas closed, and runs Freon again. The three-SCM-failure case sleeps 150 seconds for SCM stale marking before checking states.

State and persistence behavior: blockade network topology and datanode container metadata are the main state. The test intentionally observes divergent local replica state while partitions exist.

Dependencies and integration points: imports `time`, logging, and `OzoneCluster`; uses `Container` methods from the cluster model.

Risks: long fixed sleep increases runtime and flake risk; assumes datanode ordering and three replicas; assertions encode specific current recovery semantics.

Test signals: one SCM-reachable isolated datanode should close, two SCM-isolated peers remain open; with no SCM connectivity all replicas remain open until restore; restore closes all.
