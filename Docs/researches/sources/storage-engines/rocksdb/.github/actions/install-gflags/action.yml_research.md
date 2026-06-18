<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml

Purpose: Installs Linux gflags development headers and library for CI jobs that need gflags.

Important APIs/types/functions: runs `sudo apt-get update -y && sudo apt-get install -y libgflags-dev`.

Control flow: one bash install step before build commands.

State and persistence behavior: mutates the ephemeral runner/container package state.

Dependencies and integration points: used by candidate ARM jobs and other non-container Linux paths where gflags is not preinstalled.

Risks: requires sudo and network package repositories. Container jobs that run as root might not need sudo, so portability depends on runner image.

Test signals: downstream CMake/make detection and tools such as `trace_analyzer` confirm gflags availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml -->
