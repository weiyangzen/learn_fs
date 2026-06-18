# sources/user-network-fs/gcsfuse/tools/package_gcsfuse_docker/Dockerfile

Purpose: Docker build environment for producing gcsfuse deb and rpm packages for amd64 or arm64 Linux.

Important APIs/types/functions: build args `GCSFUSE_VERSION`, `BRANCH_NAME`, `ARCHITECTURE`, `GCSFUSE_REPO`, package build steps using `build_gcsfuse`, `dpkg-deb`, and `fpm`.

Control flow: starts from Go image, installs Ruby/fpm dependencies, validates architecture, clones and checks out gcsfuse, installs the repository's `.go-version`, builds gcsfuse into a package tree, moves binaries to `/usr/bin`, prepares Debian metadata/docs, updates version/architecture fields, gzips changelog, strips binaries, builds deb and rpm outputs under `/packages`.

State/persistence behavior: image layers contain the cloned repo, downloaded Go toolchain, built binaries, package tree, and final packages.

Dependencies/integration: used by release/package automation where host tooling is encapsulated in Docker.

Risks/test signals: `RUN PATH=$PATH:/usr/local/go/bin` does not persist as an `ENV`, though later `go version` may still find Go if base image paths remain valid. The rpm URL is built as `https://$GCSFUSE_REPO`, which can duplicate scheme when default repo already includes `https://`.
