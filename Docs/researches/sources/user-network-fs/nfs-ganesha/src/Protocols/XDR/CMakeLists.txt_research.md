# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/CMakeLists.txt

Purpose: defines the `nfs_mnt_xdr` object library that contains XDR encode/decode implementations for mount, NFSv2/v3, NFSv4.1, NLM, NSM, NFSACL, and optionally RQUOTA protocol data.

Important APIs and targets: `nfs_mnt_xdr_STAT_SRCS`, `add_library(nfs_mnt_xdr OBJECT ...)`, `add_sanitizers(nfs_mnt_xdr)`, `set_target_properties(... -fPIC)`, feature variables `USE_RQUOTA` and `USE_LTTNG`, and the generated LTTng dependency `gsh_trace_header_generate`.

Control flow: the file builds the static source list with the core XDR files, appends `xdr_rquota.c` only when `USE_RQUOTA` is enabled, creates an object library, attaches sanitizer instrumentation, forces position-independent compilation, and wires trace header generation when LTTng support is configured.

State and persistence: no runtime state. Build output is an object library consumed by higher-level ganesha targets.

Dependencies and integration points: integrates protocol XDR objects into the larger build. Conditional RQUOTA compilation must align with protocol dispatch and headers. LTTng dependencies must align with generated trace headers so trace-aware files compile after generation.

Risks: adding a protocol XDR file without updating this list omits symbols at link time. Enabling `USE_RQUOTA` without matching headers/protocol sources can break builds. Because this is an object library, consumers inherit object files rather than linking a standalone archive.

Test signals: configure builds with `USE_RQUOTA` on and off, with `USE_LTTNG` on and off, and verify `nfs_mnt_xdr` object files and dependent final targets link without missing XDR symbols.
