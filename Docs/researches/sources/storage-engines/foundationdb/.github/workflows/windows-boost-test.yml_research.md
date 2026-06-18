# sources/storage-engines/foundationdb/.github/workflows/windows-boost-test.yml

## Purpose
This workflow verifies FoundationDB CMake configuration can find Boost in CONFIG mode on Windows.

## Important APIs, Types, And Functions
The `test-windows-boost` job runs on `windows-2025`, checks out code, installs Boost components and `lz4` through vcpkg, then configures a Release build with the vcpkg toolchain, Swift/C#/docs/tests disabled.

## Control Flow
It triggers on PRs to `main` and pushes to `main` or `boost-*`. The job installs dependencies, creates `build`, runs CMake configure, and prints a success message.

## State And Persistence Behavior
It mutates only the ephemeral Windows runner and vcpkg cache/install directories.

## Dependencies And Integration Points
It depends on GitHub hosted Windows, vcpkg, CMake, FoundationDB's Boost detection, and selected build options.

## Risks And Edge Cases
`actions/checkout@v4` is not SHA-pinned here unlike other workflows. The job configures but does not build targets despite the step name, so it mainly validates dependency discovery.

## Test Signals
Failure indicates Boost CONFIG/vcpkg integration or Windows CMake configuration regression.
