## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/container.py

Purpose: object wrapper for an Ozone container ID in blockade tests, with polling helpers for expected replica states under network partitions.

Important APIs/types/functions: `Container(container_id, cluster)` delegates all inspection to `OzoneCluster`. `is_on`, `get_datanode_states`, `get_state`, and wait helpers cover `QUASI_CLOSED`, `CLOSED`, and "not OPEN" conditions. Wait helpers use `ozone.util.wait_until` with 120 second timeout and 10 second frequency.

Control flow: tests obtain `Container` instances from `cluster.get_container` or `get_containers_on_datanode`, partition the network, then call state wait helpers before asserting exact or allowed replica states. Methods catch `ContainerNotFoundError` where a not-yet-materialized replica should be treated as false.

State and persistence behavior: stores only `container_id` and `cluster`. Replica state is live data read from datanode `.container` files through the cluster helper.

Dependencies and integration points: imports `ozone.exceptions.ContainerNotFoundError`, `ozone.util.wait_until`, and uses `cluster.datanodes` plus `cluster.get_container_state`.

Risks: polling returns assertion-style failures rather than rich diagnostics; all waits share fixed timeouts; replica state strings are hard-coded; missing replicas are sometimes false and sometimes errors depending on method.

Test signals: directly validates the core expected behavior of blockade tests: open, quasi-closed, and closed container replica transitions after isolation and healing.
