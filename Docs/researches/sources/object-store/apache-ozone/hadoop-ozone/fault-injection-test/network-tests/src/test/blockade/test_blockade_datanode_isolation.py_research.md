## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_datanode_isolation.py

Purpose: pytest coverage for datanode-to-datanode isolation where one or all datanodes cannot communicate with peers while OM/SCM/client connectivity varies.

Important APIs/types/functions: `test_isolate_single_datanode` and `test_datanode_isolation_all`, with standard cluster setup/teardown. Imports `ContainerNotFoundError` for expected missing replica paths.

Control flow: tests seed a replicated container with Freon, create partitions, use `cluster.get_containers_on_datanode`, wait for one or all replicas to leave `OPEN`, assert replica states, restore network, wait for all closed, and verify Freon success. The all-isolated case checks each datanode's local view and tolerates missing container metadata during isolation.

State and persistence behavior: reads and writes Ozone container metadata on datanode disks. Network partitions are external blockade state.

Dependencies and integration points: relies on `OzoneCluster`, `Container` wait helpers, and Freon random key generation from the client container.

Risks: timing-sensitive state transitions; assumes replication factor three and three datanodes; direct disk metadata parsing can race with datanode writes; expected missing containers may mask unexpected placement changes.

Test signals: validates quasi-closed/closed convergence and post-restore all-closed replicas.
