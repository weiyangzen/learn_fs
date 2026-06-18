# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/CMakeLists.txt

Purpose: builds the NLM protocol object library used for NFSv3 locking, share reservations, NSM monitoring, async callbacks, and the standalone `sm_notify` source when included in the source list.

Important APIs/types/functions: build metadata includes `nlm_STAT_SRCS`, `add_library(nlm OBJECT ...)`, sanitizer instrumentation, `-fPIC`, and optional LTTng generated-header dependencies. The source list includes lock/test/cancel/unlock/share/unshare/null/free-all/sm-notify handlers plus `nlm_async.c`, `nlm_util.c`, and `nsm.c`.

Control flow: CMake defines and compiles all NLM protocol source files into one object library. Parent protocol build logic controls whether this directory participates.

State and persistence: no runtime state. Build output state is object files with consistent sanitizer, PIC, and trace-generation dependencies.

Dependencies and integration points: integrates with core NFS-Ganesha protocol dispatch, state/SAL, FSAL, RPC/XDR, and optional LTTng tracing through the compiled sources.

Risks and test signals: missing one source causes unresolved symbols or disabled lock semantics. Test feature-enabled builds, LTTng builds, sanitizer builds, and link checks for all NLM procedure handlers.
