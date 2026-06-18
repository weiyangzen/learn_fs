# sources/storage-engines/foundationdb/packaging/docker/samples/python/docker-compose.yml

Purpose: This Compose file launches a three-process FoundationDB cluster plus the Python Flask counter app. It is the Python counterpart to the Go sample.

Important services: Three FoundationDB services share coordinator/networking environment, with the coordinator exposing port 4500. The `app` service builds from `app`, passes `FDB_VERSION` and `FDB_ADDITIONAL_VERSIONS`, exposes port 5000, and sets `FDB_COORDINATOR` and `FDB_API_VERSION`.

Control flow: Compose dependency ordering starts the app after the three FDB services are created, but readiness is handled by the app start script and FDB client retries.

State and persistence behavior: No explicit volumes are declared, so database state is sample-ephemeral unless image volumes are retained. The Flask app persists the counter key in the running cluster.

Dependencies and integration points: It depends on the FoundationDB Docker image environment contract, Python app Dockerfile/start script, Flask, and FDB client libraries.

Risks: `depends_on` is not a readiness gate. Additional client library versions must be downloadable at build time. Tests should run compose, hit `GET /counter` and `POST /counter/increment`, and verify cluster status with `fdbcli`.
