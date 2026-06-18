<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container -->
# sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container

## Purpose
This POSIX-shell helper builds and runs Podman containers with NFS-Ganesha build dependencies for supported Linux distributions. It is intended for developers who want a repeatable build/test environment across distro versions, with special modes for listing supported versions, building/running every supported container, and deleting all generated images.

## Important APIs, Types, and Functions
The script's public interface is `ganesha-container {distro [version] | all | delete-all | list} [[--] cmd...]`. `list_versions` emits the supported matrix. `default_version` selects the current default for each distro family. `validate_distro_version` rejects unsupported pairs. `container_image` maps distro/version pairs to upstream image names, including CentOS Stream and SLE registry naming. `container_1` builds the local image tag, removes stale stopped containers, detects SELinux enforcing mode for bind-mount relabeling, and runs the container. `container_foreach` loops over the version matrix for `all` and `delete-all`.

## Control Flow
Argument parsing chooses a distro, optional version, and optional command. If a non-special distro is used without a version, `default_version` fills it in; a `--` separator is consumed before the command. `container_1` changes into the script directory so `buildah bud` can use the local `Containerfile`, creates an image tag like `ubuntu:24.04.ganesha`, then starts a one-shot `podman container run` with `--rm`, `--userns=keep-id`, a bind mount of the caller's original working directory, and an interactive login shell when no command is supplied.

## State and Persistence Behavior
Persistent state is held in local Podman/Buildah images named `<distro>:<version>.ganesha`; running containers are named `<distro><version>.ganesha` and are removed automatically. The caller's working tree is bind-mounted in place, so commands inside the container can modify repository files. `delete-all` removes generated images but does not touch source files.

## Dependencies and Integration Points
The script depends on `/bin/sh`, `podman`, `buildah`, `realpath`, `id`, `tty`, and optional `sestatus`. It integrates with `scripts/podman/Containerfile` and `install-packages.sh` through build arguments for base image and user/group ids. It is a developer-facing bridge between the NFS-Ganesha tree and distro package ecosystems.

## Risks and Test Signals
Risks include distro matrix drift, missing credentials for SLE registry access, stale running containers blocking reuse, SELinux relabeling only being enabled when `sestatus` reports enforcing, and bind-mounting the whole workdir at the same path inside the container. The `podman container inspect` assignment redirects command output, so the `running` variable receives no formatted value; that path can fail to detect the running state as intended. Test signals include `list`, default-version runs, explicit-version runs, `all true`, `delete-all`, non-TTY command execution, TTY shell launch, and SELinux enforcing/non-enforcing hosts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container -->
