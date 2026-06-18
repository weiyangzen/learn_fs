# File Research: sources/local-fs/erofs-utils/lib/liberofs_dockerconfig.h

This header declares Docker registry credential lookup support for OCI import.

Definitions:
- `DOCKER_REGISTRY`: `docker.io`
- `DOCKER_API_REGISTRY`: `registry-1.docker.io`
- `DOCKER_HUB_AUTH_KEY`: Docker Hub’s config auth key.
- `struct erofs_docker_credential` with heap-owned `username` and `password`.

API:
- `erofs_docker_config_lookup(const char *registry, struct erofs_docker_credential *cred)`
- `erofs_docker_credential_free(struct erofs_docker_credential *cred)`

Known users:
- `remotes/oci.c` uses this when CLI credentials are absent.

Ownership:
- On success, `cred->username` and `cred->password` must be released through `erofs_docker_credential_free()`, which scrubs sensitive memory in the implementation.
