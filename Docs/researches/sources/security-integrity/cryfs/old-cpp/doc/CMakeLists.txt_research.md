# sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt

Purpose: Builds and installs compressed Unix man pages for `cryfs` and `cryfs-unmount`.

Important APIs and types: Uses `GNUInstallDirs`, `find_program(GZIP gzip)`, two `add_custom_command` calls, two `add_custom_target(... ALL ...)`, and an `install(FILES ... DESTINATION ${CMAKE_INSTALL_MANDIR}/man1 CONFIGURATIONS Release)`.

Control flow: On Windows it logs that man pages are not installed. On other platforms it finds gzip, generates `cryfs.1.gz` and `cryfs-unmount.1.gz` in the binary dir from source man pages, attaches both to the default build, and installs them only for Release configuration.

State and persistence behavior: Writes compressed man pages into the build directory and installs them under the configured man directory during install.

Dependencies and integration points: Added by `src`/top-level documentation build flow. It depends on gzip and the source files under `doc/man`.

Risks: `find_program(GZIP gzip)` does not explicitly fail if gzip is missing before custom command execution. Install is Release-only, so Debug installs omit man pages. Shell redirection in `COMMAND ${GZIP} -c ... > ...` depends on CMake command invocation semantics.

Test signals: Build target `man`/`umountman` generation and package/install contents containing both gzipped man pages are the key signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt` completely for this pass (26 lines, 882 bytes).
