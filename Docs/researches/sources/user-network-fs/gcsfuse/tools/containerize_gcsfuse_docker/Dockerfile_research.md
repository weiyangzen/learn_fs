<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile -->
# sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile

Purpose: Multi-stage Dockerfile for building container images with gcsfuse installed, including a distroless runtime target and an Ubuntu/Debian runtime target.

Important APIs, types, and functions: Build args include `GO_VERSION`, `OS_VERSION`, `OS_NAME`, `GCSFUSE_VERSION`, `GCSFUSE_REPO`, and `BRANCH_NAME`. Stage `gcsfuse-package` clones gcsfuse, checks out a branch/tag, installs fpm via bundler, builds gcsfuse using `build_gcsfuse`, and packages a `.deb`. The `distroless` stage copies gcsfuse, mount helper, fusermount, and shell. The final OS stage installs the generated deb and fuse.

Control flow: Docker builds the package stage first. Consumers can target `distroless` explicitly or build the final Ubuntu/Debian image by supplying OS args. Both runtime targets define `CMD gcsfuse --key-file /key.json ... $BUCKET_NAME /gcs`.

State and persistence behavior: Build-time state includes cloned source, generated binaries, and package files. Runtime mounts a bucket into `/gcs` and expects host/container mount propagation and privileged FUSE access.

Dependencies and integration points: Depends on golang base image, Debian apt, Ruby/fpm packaging, GitHub source, gke distroless libc image, FUSE, and host Docker run options described in comments. Integrates with release/container samples rather than the Go test suite.

Risks and test signals: Requires privileged containers and key file mount. Final OS stage copies `*amd64.deb`, so non-amd64 builds may not work there. Distroless includes `/bin/sh` copied from build stage, which may be surprising. Runtime command uses environment variable expansion in shell form only if interpreted as shell; Dockerfile `CMD` shell form is used, so variable expansion is expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/containerize_gcsfuse_docker/Dockerfile -->
