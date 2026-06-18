<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt

Purpose: top-level documentation build gate.

Important build surface: if `USE_MAN_PAGE` is enabled, it adds the `man` subdirectory. Otherwise no documentation targets are created from this directory.

Control flow/state: CMake-only conditional; no runtime state.

Dependencies/integration: integrates the Sphinx man-page build into the main CMake tree through `src/doc/man/CMakeLists.txt`. Controlled by the `USE_MAN_PAGE` option.

Risks: disabling `USE_MAN_PAGE` silently skips manpage generation and installation. Any packaging expecting generated man pages must ensure the option and Sphinx dependencies are present.

Test signals: configure with `-DUSE_MAN_PAGE=ON` and verify the `manpages` target appears; configure with it off and verify the docs directory does not add build requirements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt -->
