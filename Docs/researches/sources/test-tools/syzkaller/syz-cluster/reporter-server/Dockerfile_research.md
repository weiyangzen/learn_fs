## sources/test-tools/syzkaller/syz-cluster/reporter-server/Dockerfile

This Dockerfile packages the `reporter-server` binary. It uses the common `syz-cluster-build` image as a builder source, then copies `/build/syz-cluster/bin/reporter-server` into a minimal Alpine runtime, exposes port 8080, and sets the binary as entrypoint.

The image depends on build args `IMAGE_PREFIX` and `IMAGE_TAG` defaulting to `local/` and `latest`. There is no runtime package installation, so the binary must be fully self-contained for Alpine. Integration is with the reporter-server Kubernetes deployment. Risks include libc/static-link assumptions and no explicit non-root user.
