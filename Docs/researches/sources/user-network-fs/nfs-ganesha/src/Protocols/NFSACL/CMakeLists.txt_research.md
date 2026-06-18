# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/CMakeLists.txt

Purpose: builds the optional NFSACL protocol object library. It defines `nfsacl_STAT_SRCS` as `nfsacl_Null.c`, `nfsacl_getacl.c`, and `nfsacl_setacl.c`, then creates the `nfsacl` object target.

Important APIs/types/functions: this file contributes build metadata rather than C APIs. Its important integration points are `add_library(nfsacl OBJECT ...)`, `add_sanitizers(nfsacl)`, `set_target_properties(... -fPIC)`, and optional LTTng trace-header dependency wiring.

Control flow: parent protocol CMake logic enters this directory only when `USE_NFSACL3` is enabled. The target is compiled as position-independent object code and later linked into the daemon/library aggregate.

State and persistence: no runtime state. Build state includes target properties, sanitizer instrumentation, and generated trace header dependency ordering when `USE_LTTNG` is set.

Dependencies and integration points: integrates with the top-level `Protocols/CMakeLists.txt` feature flag and the generated LTTng property include under the binary directory.

Risks and test signals: build omissions here remove RPC handlers even if XDR/procedure tables expect them. Test by configuring with and without `USE_NFSACL3`, with sanitizers and LTTng enabled, and verifying `nfsacl` object files are linked only in the enabled build.
