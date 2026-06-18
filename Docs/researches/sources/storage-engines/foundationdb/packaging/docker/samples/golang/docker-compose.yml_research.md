# sources/storage-engines/foundationdb/packaging/docker/samples/golang/docker-compose.yml

Purpose: This Compose file launches a three-process FoundationDB cluster plus the Go counter application. It demonstrates app-to-cluster connectivity in containers.

Important services: `fdb-coordinator`, `fdb-server-1`, and `fdb-server-2` use `foundationdb/foundationdb:${FDB_VERSION}` with coordinator/networking environment. `app` builds from `app`, passes `FDB_VERSION`, exposes port 8080, and sets `FDB_COORDINATOR` and `FDB_API_VERSION`.

Control flow: Server containers start with dependency ordering, and the app depends on all three FDB services. The coordinator exposes port 4500 to the host.

State and persistence behavior: The Compose file does not define persistent volumes, so database state is container-local/ephemeral unless Docker image defaults create volumes elsewhere. The app persists counter state in the cluster while it exists.

Dependencies and integration points: It relies on the FoundationDB Docker image's environment contract and the Go app Dockerfile/start script. It forces `linux/amd64` platform for all services.

Risks: `depends_on` does not wait for FDB readiness, so the app start script must handle configuration races. Tests should run `docker compose up`, wait for `/counter`, and verify multi-container cluster status.
