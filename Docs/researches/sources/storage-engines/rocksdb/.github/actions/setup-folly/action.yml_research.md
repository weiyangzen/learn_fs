<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml

Purpose: Prepares Folly sources and Linux packages needed before building RocksDB with Folly.

Important APIs/types/functions: runs `make checkout_folly`; installs `patchelf` and `libaio-dev` with apt.

Control flow: source checkout happens first, then system packages are installed.

State and persistence behavior: populates `third-party/folly` and mutates ephemeral package state.

Dependencies and integration points: used by Folly PR/nightly jobs before `cache-folly` and `build-folly`. Depends on make targets and Debian package repositories.

Risks: checkout target and package availability are external failure points. No retry or cache logic exists in this action itself.

Test signals: existence of Folly source tree and successful later `make build_folly` or Folly-enabled CMake/make builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml -->
