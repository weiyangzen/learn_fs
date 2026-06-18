# sources/storage-engines/foundationdb/packaging/docker/samples/local/docker-compose.yml

Purpose: This Compose file runs a one-node FoundationDB cluster that is accessible from the host. It is the minimal local sample.

Important service: `fdb` uses image `foundationdb:6.1.8`, maps `$FDB_PORT` to the same container port, and sets `FDB_NETWORKING_MODE=host`, `FDB_COORDINATOR_PORT`, and `FDB_PORT`.

Control flow: Compose starts only the FDB service. Companion `start.bash` and `stop.bash` handle cluster-file creation and lifecycle.

State and persistence behavior: No explicit volumes are declared, so state is ephemeral unless Docker image volumes are retained. The host cluster file is written by `start.bash`, not by this YAML.

Dependencies and integration points: It integrates with local Docker Compose and host `fdbcli`. It pins an old sample image version.

Risks: The image tag lacks the `foundationdb/foundationdb` namespace used in newer samples and may not exist locally. Host networking mode here is represented through environment, not Docker `network_mode`. Tests should run the companion scripts and verify host `fdbcli` can connect through the generated cluster file.
