# sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/Dockerfile

Purpose: This Dockerfile builds the Go sample application image that talks to a FoundationDB Docker cluster. It installs FDB clients into a Go build image and compiles the sample HTTP app.

Important operations: It uses an `FDB_VERSION` build arg, references the FoundationDB image as a stage, starts from `golang:1.22`, installs `ca-certificates` and `dnsutils`, downloads the matching `foundationdb-clients` Debian package from GitHub releases, installs it with `dpkg`, copies the app, runs `go get` and `go install`, and sets `/start.bash` as the command.

Control flow: Build-time steps are linear and depend on release artifact availability for the requested version.

State and persistence behavior: The image persists installed FDB client libraries/tools, Go source/build output, and the start script. Runtime persistence is handled by the FDB cluster, not this image.

Dependencies and integration points: It integrates with the adjacent Go `main.go`, `start.bash`, and sample `docker-compose.yml`. `dnsutils` supports cluster-file creation in the start script.

Risks: It downloads only `amd64` Debian packages while compose forces `linux/amd64`; multi-arch users need changes. `go get` during build can be non-reproducible without pinned modules. Tests should build for the sample version and hit the `/counter` endpoint against the compose cluster.
