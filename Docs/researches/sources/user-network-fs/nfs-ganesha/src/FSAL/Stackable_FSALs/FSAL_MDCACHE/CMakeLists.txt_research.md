# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/CMakeLists.txt

## Purpose

This CMake file builds the MDCACHE stackable FSAL object library. MDCACHE wraps a sub-FSAL and caches metadata, handles, dirents, and related state for NFS-Ganesha. The source was read as a complete 64-line file.

## Important APIs, Types, and Functions

The target is `fsalmdcache` as an `OBJECT` library. `fsalmdcache_LIB_SRCS` includes core headers and implementation files such as `mdcache_handle.c`, `mdcache_file.c`, `mdcache_xattrs.c`, `mdcache_main.c`, `mdcache_export.c`, `mdcache_helpers.c`, `mdcache_lru.c`, `mdcache_hash.c`, `mdcache_avl.c`, `mdcache_read_conf.c`, and `mdcache_up.c`. It adds `-D__USE_GNU`, optional DBus includes, sanitizer instrumentation, `-fPIC`, and optional LTTng trace dependencies/properties.

## Control Flow

At configure time it collects sources, creates the object library, applies sanitizer and PIC flags, and wires LTTng generation if enabled. No executable control flow is present.

## State and Persistence Behavior

No runtime state is directly owned, but the selected sources implement MDCACHE global parameters, LRU/hash partitions, export maps, dirent chunks, upcalls, and object operations.

## Dependencies and Integration Points

It depends on global build options `USE_DBUS` and `USE_LTTNG`, DBus include variables, generated trace property files, and the wider FSAL build that links this object library into NFS-Ganesha.

## Risks and Edge Cases

Object-library source-list drift can omit a cache component while still compiling other FSAL code. LTTng generation ordering must be correct or trace headers will be missing. `LIB_PREFIX` is set but not used locally.

## Test Signals

Configure and build with DBus/LTTng toggled, verify all listed MDCACHE sources compile as PIC, and run link tests that consume the object library from the final daemon/module target.
