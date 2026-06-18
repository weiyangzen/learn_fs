# sources/sync-backup/syncthing/Dockerfile

Purpose: multi-stage Dockerfile for the Syncthing runtime image. It optionally builds the Syncthing binary in a Go builder stage and then packages it into an Alpine-based runtime image.

Important APIs/types/functions: build args include `GOVERSION`, `BUILD_USER`, `BUILD_HOST`, and `TARGETARCH`. The builder checks for a prebuilt `syncthing-linux-$TARGETARCH`; otherwise it runs `go run build.go -no-upgrade build syncthing` and renames the result. Runtime metadata includes OCI labels, exposed GUI/sync/discovery ports, `/var/syncthing` volume, `PUID/PGID/HOME`, `STGUIADDRESS`, and `STHOMEDIR`.

Control flow: Docker always pulls a Go image because Dockerfile sections cannot be conditional. The runtime stage installs certificates, curl, libcap, su-exec, and tzdata, copies the binary and entrypoint, defines a healthcheck against `/rest/noauth/health`, and starts `/bin/entrypoint.sh /bin/syncthing`.

State and persistence behavior: persistent container data lives under `/var/syncthing`, with config at `/var/syncthing/config`. Image build state is discarded between stages except for the copied binary and entrypoint.

Dependencies/integration: integrated with GitHub Docker jobs, `build.go`, `script/docker-entrypoint.sh`, Alpine packages, and multi-arch `TARGETARCH`.

Risks/test signals: relying on `TARGETARCH` naming requires buildx/platform consistency. `CGO_ENABLED=0` in builder affects sqlite/build-tag choices compared to CGO release packages. Signals are successful multi-arch image builds, a healthy container endpoint, and correct persisted config ownership through entrypoint handling.
