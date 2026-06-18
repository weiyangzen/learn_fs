# sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt

Purpose: Top-level source directory CMake file that adds all legacy C++ subprojects to the build.

Important APIs and types: Calls `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` and `add_subdirectory` for `gitversion`, `cpp-utils`, `fspp`, `parallelaccessstore`, `blockstore`, `blobstore`, `cryfs`, `cryfs-cli`, `cryfs-unmount`, and `stats`.

Control flow: During configure, each subdirectory is added in dependency order close to bottom-up library layering.

State and persistence behavior: No files are written directly. It mutates include directory state globally for descendants.

Dependencies and integration points: This is the source-tree build entry for the old C++ product and libraries. Blockstore in this subset is one of the subdirectories registered here.

Risks: Global `include_directories` is broad and can mask include hygiene issues. Subdirectory order matters because later targets may expect earlier targets.

Test signals: Full CMake configure/build success validates that all subprojects can be discovered and ordered correctly.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt` completely for this pass (12 lines, 333 bytes).
