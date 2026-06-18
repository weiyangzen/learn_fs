# sources/user-network-fs/nfs-ganesha/src/scripts/docker/Dockerfile-in.cmake

## Purpose
This CMake-templated Dockerfile builds a simple NFS-Ganesha container image. CMake substitutes the base distribution/version and install prefix, Docker installs runtime prerequisites, copies a prepared `root/` filesystem, creates the Ganesha log directory, copies the entrypoint, and sets it as the container entrypoint.

## Important APIs, Types, And Functions
The file uses Dockerfile primitives: `FROM`, `MAINTAINER`, `RUN`, `ADD`, and `ENTRYPOINT`. Its template API is `@DOCKER_DISTRO@`, `@DOCKER_DISTRO_VERSION@`, and `@CMAKE_INSTALL_PREFIX@`.

## Control Flow
At build time Docker resolves the configured base image, runs DNF installs, adds `root/` to `/`, creates `@CMAKE_INSTALL_PREFIX@/var/log/ganesha`, adds `/entrypoint.sh`, and records `ENTRYPOINT ["/entrypoint.sh"]`. Runtime control passes to the generated entrypoint script.

## State And Persistence
The image persists installed RPMs, copied root filesystem content, `/entrypoint.sh`, and the log directory. It declares no volumes or runtime defaults beyond the entrypoint.

## Dependencies And Integration Points
It assumes a DNF-based base image. Runtime packages include `libcap`, `libblkid`, `libuuid`, `dbus`, `nfs-utils`, `rpcbind`, `libnfsidmap`, and `libattr`; prerequisite packages include `tar` and `redhat-lsb-core`. It integrates with the CMake install tree through `root/` and with `entrypoint.sh-in.cmake` through the generated entrypoint.

## Risks And Edge Cases
`dnf` hard-codes Fedora/RHEL-like images. `MAINTAINER` is deprecated. `ADD root/ /` can bake unexpected artifacts into the image. DNF metadata is not cleaned. The image does not define users, volumes, or runtime capabilities, so NFS service execution likely depends on privileged/root container flags.

## Test Signals
Verify CMake substitution removes all `@...@` tokens, then build with Docker/Podman. Smoke tests should confirm `/entrypoint.sh`, `ganesha.nfsd`, RPC helpers, and the configured log directory exist.
