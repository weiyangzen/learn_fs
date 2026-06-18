## sources/distributed-fs/xrootd/src/XrdNet/CMakeLists.txt

Purpose: Registers XrdNet source and header files as private sources of the `XrdUtils` target.

Important APIs and functions: Uses CMake `target_sources(XrdUtils PRIVATE ...)` to list network core, address, buffer, cache, notification, connect, identity, interface, messaging, PMark, refresh, registry, security, socket, and utility compilation units.

Control flow: No runtime control flow. Build configuration simply feeds the listed files into the `XrdUtils` target.

State and persistence: No runtime state or persistence. The file persists build membership and therefore controls whether implementation files are compiled into the utility library.

Dependencies and integration points: Integrates XrdNet into the broader XRootD CMake build through `XrdUtils`. Headers are included in the source list for IDE visibility and dependency tracking; implementations rely on system socket APIs and XRootD support libraries.

Risks: Missing a `.cc` file here can produce unresolved symbols; listing headers as private sources does not export include paths by itself. PMark is split across adjacent files, so partial build-list changes can silently break optional packet marking features.

Test signals: Configure and build `XrdUtils`; verify every listed implementation compiles on Linux and Windows-gated code paths; check incremental builds notice header changes.
