# sources/storage-engines/foundationdb/.devcontainer/devcontainer.json

## Purpose
This JSON file defines a VS Code/devcontainer environment for FoundationDB development.

## Important APIs, Types, And Functions
It selects image `docker.io/foundationdb/build:rockylinux9-latest`, enables `SYS_PTRACE`, privileged mode, unconfined seccomp, and a 60 GB storage requirement. It sets `CC=clang`, `CXX=clang++`, and `BOOST_ROOT=/opt/boost_1_78_0_clang`. VS Code extensions include clangd and CMake Tools, with CMake configured to export compile commands.

## Control Flow
There is no executable control flow. The devcontainer runtime reads the JSON and provisions the container.

## State And Persistence Behavior
The file influences container state and build environment but does not store application data.

## Dependencies And Integration Points
It integrates with VS Code Remote Containers, the FoundationDB build image, CMake, clang, and Boost.

## Risks And Edge Cases
Privileged mode and unconfined seccomp expand container permissions. The pinned Boost path must match the image. Storage below 60 GB may fail builds.

## Test Signals
Validation is by opening the devcontainer and configuring/building FoundationDB successfully.
