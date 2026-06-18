# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/CMakeLists.txt

Purpose: Builds the in-memory MEM FSAL as a Ganesha loadable module.

Important APIs and types: The build target is `fsalmem`, a `MODULE` library composed from `mem_export.c`, `mem_handle.c`, `mem_int.h`, `mem_main.c`, and `mem_up.c`. It defines `-D__USE_GNU`, links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, `${LTTNG_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, applies sanitizers, and installs to `${FSAL_DESTINATION}`.

Control flow: CMake declares source list, creates the module, attaches sanitizers, links required libraries, sets version `4.2.0` and SOVERSION `4`, and installs the artifact as FSAL component.

State and persistence: No runtime state. The file determines which MEM FSAL implementation units and trace dependencies are present in the plugin.

Dependencies and integration: Tightly integrated with the Ganesha server library because it links `ganesha_nfsd` directly. Optional LTTng tracing libraries are linked through `${LTTNG_LIBRARIES}`.

Risks: `LDFLAG_DISALLOW_UNDEF` makes missing symbols fail link, useful for module quality but sensitive to platform link rules. Version/SOVERSION must match package expectations. Missing LTTng variable setup can affect builds depending on parent CMake defaults.

Test signals: Build with tracing enabled/disabled, sanitizer builds, undefined-symbol checks, install path packaging, and Ganesha startup with `fsalmem` loaded.
