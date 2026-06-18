<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh

Purpose: discovers or installs usable `cmake` and `ctest` binaries for Evergreen and spawn-host environments.

Control flow: defines fallback CMake version 3.13.0 and `find_cmake()`. The function honors existing `CMAKE`, then checks MongoDB toolchain, Homebrew, CMake.app, `/opt/cmake`, `cmake3`, `cmake`, downloaded Linux binary tarball, Cygwin path, and previous `cmake-install`. If no working CMake is found, it downloads CMake source, bootstraps, builds, and installs under `cmake-install`. It prints paths and versions for both CMake and CTest.

State and persistence: may download `cmake.tar.gz`, create `cmake-3.13.0`, and create `cmake-install`. Exports shell variables only in the running shell when sourced; when executed they affect the script process only.

Dependencies and integration: called or sourced by many Evergreen scripts before configure/build steps.

Risks and test signals: source build is expensive. The ERR trap returns from the function on failure and is cleared at the end. Version 3.13.0 is old for some modern platforms, so earlier path checks matter. Success is visible through printed command paths and version output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh -->
