# sources/user-network-fs/nfs-ganesha/src/scripts/podman/Containerfile

## Purpose

This Containerfile builds a development/test container image from a caller-supplied base image, installs packages, and creates a non-root user matching supplied host UID/GID.

## Important APIs, Types, and Functions

Build args are `IMAGE`, `USER_ID`, and `GROUP_ID`. The file copies `install-packages.sh` to `/tmp`, runs it, removes any existing `ubuntu` user/group, creates group/user `user`, configures passwordless sudo in `/etc/sudoers.d/container`, and switches to `USER user`.

## Control Flow

The build starts from `FROM $IMAGE`, runs package installation as root, adjusts user/group identity, writes sudo policy, and leaves subsequent container commands running as the created user.

## State and Persistence Behavior

The image persists installed packages, the created user/group/home directory, and sudoers file. Runtime container state is not handled here.

## Dependencies and Integration Points

It depends on a valid base image, build args, `install-packages.sh` in the build context, and Linux user-management utilities. It is intended for Podman but is also Dockerfile-like.

## Risks and Edge Cases

Missing build args can make `FROM`, `groupadd`, or `useradd` fail. If the base image lacks `userdel`, `groupdel`, `groupadd`, `useradd`, or sudo support, the build fails. The sudoers file permissions are not explicitly set. Removing `ubuntu` may be harmless but base-image-specific.

## Test Signals

Container build tests should pass representative base images and UID/GID values, verify package installation, user identity, sudoers behavior, and non-root default user.
