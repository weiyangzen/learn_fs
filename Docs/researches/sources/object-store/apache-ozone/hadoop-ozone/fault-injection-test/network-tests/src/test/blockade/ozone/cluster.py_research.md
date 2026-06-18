## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/cluster.py

Purpose: docker-compose/blockade backed Ozone test cluster harness for network fault-injection tests. It discovers container names, starts/scales/stops the cluster, and exposes helpers for inspecting datanode container replicas.

Important APIs/types/functions: `Configuration` selects `docker-compose.yaml` from `MAVEN_TEST`, `OZONE_HOME`, or a relative compose path and sets `DOCKER_COMPOSE_FILE`. `OzoneCluster.create/start/stop` manage lifecycle. Properties expose `om`, `scm`, `datanodes`, and `client`. Helpers include `get_conf_value`, `scale_datanode`, `partition_network`, `restore_network`, `get_client`, `get_container`, `is_container_replica_exist`, `get_containers_on_datanode`, `get_container_state`, and `get_container_datanodes`.

Control flow: `start` validates `OZONE_RUNNER_VERSION` and `HDDS_VERSION`, destroys an existing blockade environment if present, runs `blockade up`, launches docker-compose with scaled datanodes, sleeps for startup, parses `docker-compose ps`, adds all containers to blockade, records OM/SCM/datanodes/client, discovers SCM UUID, and reads datanode data directory. Replica inspection walks datanode disk files under `hdds/<scmUuid>/current/containerDir0` and parses `.container` YAML-ish metadata.

State and persistence behavior: mutates docker-compose containers, blockade network state, and Ozone on-disk datanode state. Python object state caches container names, SCM UUID, and datanode directory.

Dependencies and integration points: uses docker-compose, blockade, PyYAML, Ozone CLI, SCM CLI, local `Blockade`, `OzoneClient`, `Container`, and `ContainerNotFoundError`. Tests use the global `cluster` fixture-style variable.

Risks: Python 2 idioms (`filter()[0]`, `output.split` on bytes/string assumptions, `is not 0`) are fragile on Python 3; `yaml.load` lacks a safe loader; fixed sleeps can flake; shell commands embed paths and IDs directly; default argument `Configuration()` is constructed at import time.

Test signals: every blockade test depends on successful `start`, partition restore, and replica state parsing.
