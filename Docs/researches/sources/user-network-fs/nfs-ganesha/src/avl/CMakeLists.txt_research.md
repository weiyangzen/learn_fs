# sources/user-network-fs/nfs-ganesha/src/avl/CMakeLists.txt

Purpose: Defines the build target for the embedded `avltree` object library used by Ganesha's tree data structures.

Important APIs/types/functions: Sets `avltree_STAT_SRCS` to `avl.c`, `bst.c`, `rb.c`, and `splay.c`; creates `add_library(avltree OBJECT ...)`; applies `add_sanitizers(avltree)`; sets `COMPILE_FLAGS "-fPIC"`; and, when `USE_LTTNG` is enabled, adds dependency on `gsh_trace_header_generate` and includes generated trace file properties.

Control flow: During CMake configure/generate, this file collects the four C source files into an object library so other targets can consume the compiled objects. Sanitizer instrumentation and PIC compilation are configured immediately on the target.

State and persistence behavior: No runtime state or persistence; build metadata only.

Dependencies and integration points: Depends on top-level sanitizer helper macros and optional LTTng generation state. The object library likely feeds shared/static Ganesha targets that need tree implementations without producing a standalone installed library here.

Risks: Forced `-fPIC` through `COMPILE_FLAGS` can interact awkwardly with toolchain-level flags. If `USE_LTTNG` generated property files are absent or stale, configure/build can fail. The file does not install headers or library artifacts directly.

Test signals: Configure with and without `USE_LTTNG`, with sanitizer options enabled, and verify downstream targets link object files from all four sources.
