## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/CMakeLists.txt

Purpose: builds the 9P protocol implementation as an object library.

APIs and flow: `9p_STAT_SRCS` enumerates all 9P interpreter, helper, config, protocol operation, xattr, I/O, and error source files. `add_library(9p OBJECT ...)` creates the object target, `add_sanitizers(9p)` applies sanitizer settings, and compile flags force `-fPIC`. When `USE_LTTNG` is enabled it depends on generated trace headers and includes generated file properties.

State/dependencies: build-time dependency surface for every 9P source in this subset; included only by parent CMake when `USE_9P` is set.

Risks/tests: missing a new handler here causes link/dispatch failures even if opcode table is updated. Test configure/build with `USE_9P` on/off, sanitizer builds, and LTTng-enabled builds.
