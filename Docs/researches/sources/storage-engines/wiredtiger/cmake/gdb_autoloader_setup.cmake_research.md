# sources/storage-engines/wiredtiger/cmake/gdb_autoloader_setup.cmake

## Purpose
`gdb_autoloader_setup.cmake` installs build-directory GDB helper scripts for Linux shared-library builds.

## Important APIs, Types, And Functions
The function `setup_gdb_autoloader` creates `copy-autoload-script` and `copy-runtime-files` custom targets when `WT_LINUX` and `ENABLE_SHARED` are true.

## Control Flow
On eligible builds, it copies `tools/gdb/load_gdb_scripts.py` to a GDB-recognized name based on `libwiredtiger.so.<version>-gdb.py`, and copies the `tools/gdb/gdb_scripts` directory into the build directory. Otherwise it emits a status message and does nothing.

## State And Persistence Behavior
It creates build artifacts in the binary directory, not installed artifacts. The copied file names must match the shared library version for GDB auto-loading.

## Dependencies And Integration Points
It depends on version variables, `WT_LINUX`, `ENABLE_SHARED`, CMake custom targets, and the source tree's `tools/gdb` directory. It is invoked by the top-level build to improve debugging.

## Risks
The function assumes Linux has GDB and that the shared library versioned filename matches the copied autoload script. Static or non-Linux builds do not get these scripts.

## Test Signals
Configure Linux shared and static builds; verify copy targets exist only for shared Linux and that GDB auto-loads the generated script when loading the built library.
