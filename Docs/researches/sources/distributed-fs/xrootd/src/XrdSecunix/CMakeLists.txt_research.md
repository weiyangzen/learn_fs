# sources/distributed-fs/xrootd/src/XrdSecunix/CMakeLists.txt

Purpose: build description for the Unix security plugin.

Important targets: sets module target name `XrdSecunix-${PLUGIN_VERSION}`, builds it from `XrdSecProtocolunix.cc`, links privately to `XrdUtils`, adds it to the `plugins` aggregate target, and installs the module library.

Control flow: no conditional branches; the Unix plugin is always built when this directory is included.

State and persistence: no runtime state. It controls target naming and install layout.

Dependencies and integration: depends on repository-level plugin version and standard install variables. The module exports the security plugin ABI implemented in the `.cc`.

Risks: minimal CMake means no direct tests or platform guards here; portability issues surface in the implementation.

Test signals: configure/build, confirm module output name and install path, and run plugin loading smoke tests.
