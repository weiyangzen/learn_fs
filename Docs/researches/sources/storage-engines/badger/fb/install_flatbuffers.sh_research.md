# sources/storage-engines/badger/fb/install_flatbuffers.sh

## Purpose
`fb/install_flatbuffers.sh` installs the FlatBuffers compiler for regenerating Badger's generated Go metadata bindings.

## Important APIs, Types, and Functions
- `install_mac`: requires Homebrew and runs `brew install flatbuffers`.
- `install_linux`: checks for `curl`, `cmake`, `g++`, and `make`; creates a temp build dir; fetches the latest FlatBuffers release from GitHub; builds and tests it; copies `flatc` to `/usr/local/bin`.
- OS dispatch through lowercased `uname -s` for `linux` and `darwin`.

## Control Flow and State
The script exits on errors. Linux installation runs inside `sudo bash -c` with the function body injected. It downloads the current latest release at runtime and removes its temp directory after copying `flatc`.

## Persistence Behavior
It installs `/usr/local/bin/flatc`, changing system state outside the repository. It does not modify Badger source directly unless called by `gen.sh` and followed by generation.

## Dependencies and Integration Points
Used by `gen.sh` when `flatc` is missing. Depends on network access, GitHub release API format, build tooling, sudo permissions, and Homebrew on macOS.

## Risks and Edge Cases
Using "latest" makes builds non-reproducible. `grep -oP` is GNU-specific and may not work everywhere. `sudo` and `/usr/local/bin` writes are unsuitable for locked-down CI. No default branch handles unsupported OS values.

## Test Signals
No automated tests. Failures surface when regenerating FlatBuffers code.
