## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/compose/docker-compose.yaml

Purpose: docker-compose topology for Ozone network fault-injection tests.

Important APIs/types/functions: defines services `datanode`, `om`, `scm`, and `ozone_client`. Each uses `${docker.image}` and `./docker-config`. Commands are `/opt/hadoop/bin/ozone datanode`, `om`, `scm`, while `ozone_client` runs `tail -f /etc/passwd` as an idle command target for `docker exec`.

Control flow: `OzoneCluster.start` invokes docker-compose with `--scale datanode=<count>`, then adds all service containers to blockade. `om` and `scm` use `ENSURE_*_INITIALIZED` environment variables to wait for metadata version files.

State and persistence behavior: compose creates runtime containers and Ozone metadata/data volumes inside them according to image defaults and `docker-config`.

Dependencies and integration points: consumed by Maven/network test harness through `MAVEN_TEST` or by local `OzoneCluster.Configuration`.

Risks: compose version 3 and unpinned exposed ports can conflict with local environments; client service is intentionally long-running but not an Ozone daemon; `${docker.image}` must be supplied.

Test signals: if this topology fails, all blockade tests fail before partition logic.
