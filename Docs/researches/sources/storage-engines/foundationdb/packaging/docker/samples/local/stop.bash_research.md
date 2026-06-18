# sources/storage-engines/foundationdb/packaging/docker/samples/local/stop.bash

Purpose: This helper stops the local Docker Compose FoundationDB sample.

Important operations: It defaults `FDB_PORT=4550`, passes that environment to `docker-compose down`, and prints that the cluster is down.

Control flow: Strict mode is enabled; any Compose failure aborts the script.

State and persistence behavior: It removes/stops Compose-managed containers and networks according to `docker-compose down`. It does not delete the generated host cluster file.

Dependencies and integration points: It depends on `docker-compose` and the adjacent compose file. The `FDB_PORT` environment matches `start.bash`.

Risks: It does not remove volumes explicitly, so Docker-managed volume behavior depends on the compose/image configuration. Tests should verify it stops the service and leaves or removes state as intended.
