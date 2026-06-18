# sources/user-network-fs/nfs-ganesha/src/cmake/rpmtools_config.cmake

## Purpose

`rpmtools_config.cmake` defines RPM metadata for packaging NFS-Ganesha.

## Important APIs, Types, and Functions

It sets variables including `RPM_NAME`, `PACKAGE_VERSION`, `RPM_SUMMARY`, `RPM_RELEASE_BASE`, `RPM_RELEASE`, `RPM_PACKAGE_LICENSE`, `RPM_PACKAGE_GROUP`, `RPM_URL`, `RPM_CHANGELOG_FILE`, and `RPM_DESCRIPTION`.

## Control Flow

At configure time, it derives `PACKAGE_VERSION` from `${PROJECT_NAME}_MAJOR_VERSION`, `${PROJECT_NAME}_MINOR_VERSION`, and `${PROJECT_NAME}_PATCH_LEVEL`. It derives `RPM_RELEASE` from `RPM_RELEASE_BASE` and `_GIT_HEAD_COMMIT_ABBREV`, then sets static descriptive metadata.

## State and Persistence Behavior

State is CMake packaging variable state consumed by rpm tooling. It does not write files directly.

## Dependencies and Integration Points

It depends on project version variables and Git revision metadata. It integrates with RPM generation modules or scripts that read the `RPM_*` variables and `rpm_changelog`.

## Risks and Edge Cases

If `_GIT_HEAD_COMMIT_ABBREV` is unset, the release string can contain an empty or invalid git suffix. The license string is `LGPLv3`, while source headers often say LGPL-3.0-or-later; package policy may require exact SPDX-like wording.

## Test Signals

Generate RPM packaging metadata from a Git checkout and a source archive, then inspect the produced spec/release strings and package description. Package linting should validate license/group fields.
