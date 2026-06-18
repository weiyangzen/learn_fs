# sources/user-network-fs/nfs-ganesha/src/hashtable/CMakeLists.txt

## Purpose
This CMake file defines the `hashtable` object library for Ganesha's partitioned hash table implementation.

## Important APIs, Types, And Functions
It sets `hashtable_STAT_SRCS` to `hashtable.c`, creates `add_library(hashtable OBJECT ...)`, applies `add_sanitizers(hashtable)`, and sets `COMPILE_FLAGS` to `-fPIC`.

## Control Flow, State, And Persistence
The file has no runtime behavior. Its build-time flow creates an object library suitable for inclusion in other shared/static targets.

## Dependencies And Integration Points
When `USE_LTTNG` is enabled, the target depends on `gsh_trace_header_generate` and includes generated LTTng file properties from the build directory. This ensures trace headers/properties are generated before compiling the hashtable object.

## Risks And Test Signals
The object-library form means downstream targets control final linkage. Build failures here usually indicate sanitizer integration, trace-generation ordering, or missing headers. The explicit `-fPIC` flag is important for shared-library consumers.
