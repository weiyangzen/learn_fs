<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt

Purpose: builds the internal D-Bus support module for NFS-Ganesha.

Important build surface: adds `${DBUS_INCLUDE_DIRS}`, defines object-library source set `gshdbus_STAT_SRCS` containing `dbus_server.c`, `properties_handler.c`, `signal_handler.c`, and `dbus_heartbeat.c`, then builds `add_library(gshdbus OBJECT ...)`. It applies `add_sanitizers(gshdbus)` and compiles as PIC with `-fPIC`.

Control flow/state: no runtime control flow; it determines which D-Bus translation units are compiled into the larger daemon/library target. If `USE_LTTNG` is enabled, the object target depends on generated trace headers and includes generated file properties.

Dependencies/integration: requires CMake variables for D-Bus include dirs and optional LTTng generation. The object library is intended for linkage into Ganesha server components that expose D-Bus admin APIs and heartbeat signals.

Risks: missing DBus headers or generated LTTng files breaks builds. Object-library use means link dependencies must be supplied by the final consumer target, not here.

Test signals: configure with and without `USE_LTTNG`, verify `gshdbus` object compilation, and run daemon startup on a system bus to validate runtime linkage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt -->
