## sources/user-network-fs/gcsfuse/Dockerfile

Purpose: Builds a minimal Alpine container image with gcsfuse compiled from the repository source.

Important APIs/types/functions: build arg `GO_VERSION`; builder stage `golang:${GO_VERSION}-alpine`; installs git; copies repo to `/run/gcsfuse/`; runs `go install ./tools/build_gcsfuse` and `build_gcsfuse . /tmp <git-hash>`; runtime stage `alpine:3.21`; installs bash, CA certs, and fuse; copies `gcsfuse` and `mount.gcsfuse`; entrypoint mounts `/gcs` with `allow_other`, foreground, and implicit dirs.

Control flow: multi-stage build compiles in Go image, then copies binaries into runtime image.

State and persistence: image contains compiled binaries and FUSE runtime packages. Runtime mount affects container/host mount namespace depending on Docker flags.

Dependencies and integration points: requires build context to include `.git` because it calls `git log`; depends on repo build tool, Go version arg, Alpine package repos, and privileged/device FUSE runtime invocation.

Risks: `GO_VERSION` has no default here, so callers must pass it or use a build wrapper. `ADD .` copies all context unless `.dockerignore` excludes it. Runtime entrypoint assumes bucket argument `/gcs` and privileged FUSE setup. Alpine/fuse package compatibility matters.

Test signals: `docker build --build-arg GO_VERSION=$(cat .go-version) .` and a privileged container mount smoke test.
