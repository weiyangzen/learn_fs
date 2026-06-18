# sources/storage-engines/wiredtiger/CMakePresets.json

## Purpose
This file defines CMake presets for common WiredTiger configure/build environments, especially MongoDB toolchain compiler selections on Linux.

## Important APIs, Types, and Functions
It uses CMake Presets version 3. Configure presets include `default`, hidden `linux`, hidden `linux-v4`, `linux-gcc`, `linux-clang`, and `linux-v4-gcc`. Build preset `default` references configure preset `default` and uses `jobs: 0`.

## Control Flow, State, and Dependencies
Preset selection injects environment variable `MONGODBTOOLCHAIN_BIN` and compiler cache variables for GCC or Clang. Conditions restrict Linux-specific presets to Linux hosts. State is CMake cache generated from selected preset.

## Integration Points, Risks, and Test Signals
It integrates local/CI configure commands with expected toolchain paths. Risks are hard-coded `/opt/mongodbtoolchain` availability and no explicit binary directory. Signal is successful `cmake --preset <name>` configure.
