# sources/storage-engines/foundationdb/packaging/docker/entrypoint.bash

Purpose: This entrypoint belongs to the Kubernetes sidecar image. It optionally sources additional environment variables, then execs the Python sidecar process.

Important operations: If `ADDITIONAL_ENV_FILE` is non-empty, it runs `source $ADDITIONAL_ENV_FILE`; then it executes `/sidecar.py $*`.

Control flow: There is no validation or fallback. `exec` replaces the shell so signals go to `sidecar.py`, with `tini` configured as the image entrypoint parent in the Dockerfile.

State and persistence behavior: It does not persist state directly; sourced environment can alter sidecar runtime behavior. The sidecar writes output files according to its own configuration.

Dependencies and integration points: It depends on `/sidecar.py` and optional environment files mounted into the container. It is used by the `foundationdb-kubernetes-sidecar` Docker target.

Risks: Unquoted `source $ADDITIONAL_ENV_FILE` and `$*` can break paths/arguments with spaces and can source unintended files. Tests should run entrypoint with and without an env file and verify signal/argument propagation.
